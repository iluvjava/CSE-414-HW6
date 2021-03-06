import re

from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointment import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
CURRENT_PATIENT = None
CURRENT_CAREGIVER = None

# Used SQL Dry Statements.
CONST_SELECT_CAREGIVER_USERNAME = "SELECT * FROM Caregivers WHERE Username = %s"
CONST_GET_ALL_VACCINE = "SELECT * FROM Vaccines"
CONST_SELECT_CAREGIVER_AVAILABLE_FOR_DATE = "SELECT * FROM Availabilities WHERE Time = %s"


class bcolors:  # Enum for text warning.
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def warn(message, exception):
    print(f"{bcolors.WARNING}{message}{bcolors.ENDC}")
    if exception:
        print(f"{bcolors.WARNING}{exception}{bcolors.ENDC}")
    pass

def create_patient(tokens):
    """
        Handles the command of creating a new patient in the database,
        given the name and password for the patient.
    """
    if len(tokens) != 3:
        print(f"Tokenization failed, expect 3 tokens, but got: {tokens}")
        return  # wrong number of token
    username = tokens[1]
    password = tokens[2]
    if Util.CheckIfGoodPassword(password) is not None:
        print(Util.CheckIfGoodPassword(password))
        print(f"The password you give in is: {password}")
        return None
    ThePatient = Patient(username, password=password)
    try:
        if ThePatient.exists_in_db():
            print("Username already exists")
            return  # account with the same name already exists.
        salt = Util.generate_salt()
        hash = Util.generate_hash(password, salt)
        ThePatient.salt, ThePatient.hash = salt, hash
        ThePatient.save_to_db()
    except pymssql.Error as dbe:
        warn("Unable to save created patient to the database. ", dbe)
        return None
    except Exception as e:
        # traceback.print_exc()
        print(e)
        warn("Exception occurred while saving the account created. ")
        return None
    print(" *** Patient's Account Registered. ***")
    return


def create_caregiver(tokens):
    """
        Static method that create a caregiver instance to the care_giver table.
    """
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return
    username = tokens[1]
    password = tokens[2]
    if Util.CheckIfGoodPassword(password) is not None:
        print(Util.CheckIfGoodPassword(password))
        return None
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)
    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)
    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        warn("Create caregiver failed, Cannot save", e)
        quit()
        return None
    except Exception as e:
        print("Error:", e)
        return None
    print(" *** Account created successfully *** ")


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()
    select_username = CONST_SELECT_CAREGIVER_USERNAME
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
        return None
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
        accept tokens of the format:
        login_patient <username> <password>
    """
    global CURRENT_PATIENT
    if not(CURRENT_PATIENT is None and CURRENT_PATIENT is None):
        if CURRENT_PATIENT is not None:
            print(f"Can't login because {CURRENT_PATIENT} is currently logged in. Please logout first.")
        else:
            print(f"Can't login because {CURRENT_CAREGIVER} is currently logged in. Please logout first.")
        return None

    if len(tokens) != 3:
        print(f"Tokenization failed, expect 3 tokens from the command input, but gotten: \n{tokens}")
    username, password = tokens[1], tokens[2]
    try:   # try logging in and store the session for the login.
        ThePatient = Patient(username, password=password).get()
        print(f"Current login patient: {username}")
        CURRENT_PATIENT = ThePatient
    except pymssql.Error as e:
        warn("An database error occurred when trying to login the patient. ", e)
        quit()
        return None
    except Exception as e:
        # traceback.print_exc()
        warn("Another non database error has occurred while processing the login of the patient. ", e)
        return None
    return None


def login_caregiver(tokens):
    """
        login_caregiver <username> <password>
    """
    # check 1: if someone's (caregiver or patient or whoever) already logged-in, they need to log out first
    global CURRENT_CAREGIVER
    if CURRENT_CAREGIVER is not None or CURRENT_PATIENT is not None:
        print("Already logged-in!")
        return
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return
    username = tokens[1]
    password = tokens[2]
    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login caregiver failed")
        print("Db-Error:", e)
        quit()
        return None
    except Exception as e:
        print("Error occurred when logging in. Please try again!")
        print("Error:", e)
        return
    # check if the login was successful
    if caregiver is None:
        print("Error occurred when logging in. Please try again!")
    else:
        print("Caregiver logged in as: " + username)
        CURRENT_CAREGIVER = caregiver


def search_caregiver_schedule(tokens):
    """
        Directly communicates with the database and pull out all the available caregivers for the given
        date.
        * Output the username for the caregivers that are available for the date.
        * along with the number of available doses left for each vaccine.
    """

    if len(tokens) != 2:
        print(f"Tokenization failed, except 2 tokens but we got: {tokens}")
        return None
    date = tokens[1]
    if len(re.findall(r"\d{4}-\d{1,2}-\d{1,2}", date)) != 1:
        print(f"Don't give that, date should be in the formate of YYYY-MM-DD, but I got: {date}")
        return None
    if CURRENT_CAREGIVER is None and CURRENT_PATIENT is None:
        print("You haven't login, please login to retrieve schedule info. ")
        return None
    if not Util.CheckDateCorrect(date):
        print("The date you pass in is not a valid date to search for. ")
    cm = ConnectionManager()
    try:
        with cm as cursor:
            cursor.execute(CONST_SELECT_CAREGIVER_AVAILABLE_FOR_DATE, (date, ))
            print("------------------------------------------")
            print(f"Caregivers Available for Date: {date}")
            for row in cursor:
                print(f"- {row['Username']}")
            cursor.execute(CONST_GET_ALL_VACCINE)
            print("------------------------------------------")
            print("Vaccines         |  Dosages               ")
            for row in cursor:
                print(f"{row['Name']}  |  {row['Doses']}")
    except pymssql.Error as sqle:
        warn("SQL database exceptions when getting available schedules. Below is the Error.", sqle)
        quit()
        return None
    except Exception as e:
        warn("Non SQL database exceptions when getting available schedules.", e)
        return None
    return None


def reserve(tokens):
    """
        1. Patient performs this operation.
        2. Randomly assign a caregiver that is available at that given Date.
        3. Output the assigned caregiver and the appointment ID.
        TODO: Part 2
    """
    global CURRENT_PATIENT
    if CURRENT_PATIENT is None:
        print("Please login as a patient first. ")
        return None
    if len(tokens) != 3:
        print(f"Expect 3 tokens: Commands, Vaccine, date, but we got: {tokens}")
        return None
    Vac, AppointmentDate = tokens[1], tokens[2]

    # validate appointment.
    try:
        TheAppointment = Appointment(Vac, AppointmentDate, patient_instance=CURRENT_PATIENT)
        ValidationResults = TheAppointment.validate_appointment()
        if ValidationResults is not None:   # appointment validations failed.
            print(ValidationResults)
            return None
    except pymssql.Error as sqle:
        warn("A Database error has occurred when trying to validate the appointment.", sqle)
        return None
    except Exception as e:
        warn("A none database has occurred while trying to validate the appointment. ", e)
        return None

    # Add appointment:
    try:
        TheAppointment.add_appointment()
    except pymssql.Error as sqle:
        warn("A database error has occured while trying to add the current appointment. ", sqle)
        quit()
        return None
    except Exception as e:
        warn("A non database error has occured while trying to add the current appointment. ", e)
        return None
    print("***** Appointment Added ******")
    return None


def upload_availability(tokens):
    """
        Upload the availability for a caregiver who is currently logged in.
    """
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global CURRENT_CAREGIVER
    if CURRENT_CAREGIVER is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    if len(re.findall(r"\d{4}-\d{1,2}-\d{1,2}", date)) != 1:
        print(f"Don't give that, date should be in the formate of YYYY-MM-DD, but I got: {date}")
        return None
    try:
        d = datetime.datetime(year, month, day)
        CURRENT_CAREGIVER.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
        TODO: Extra Credit
    """


    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global CURRENT_CAREGIVER
    if CURRENT_CAREGIVER is None:
        print("Please login as a caregiver first!")
        return
    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return
    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Failed to get Vaccine information")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to get Vaccine information")
        print("Error:", e)
        return
    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Failed to add new Vaccine to database")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Failed to add new Vaccine to database")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Failed to increase available doses for Vaccine")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Failed to increase available doses for Vaccine")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    """
        Show info about appointment only for the current user.
        * If user is a caregiver then:
            you should print the appointment ID, vaccine name, date, and patient name.
        * if the user is a patient then:
            For patients, you should print the appointment ID, vaccine name, date, and caregiver name.
        TODO: TEST IT.
    """
    if CURRENT_PATIENT is None and CURRENT_CAREGIVER is None:
        print("Please at least loging as a caregiver, or a patient to executed this command. ")
    if len(tokens) > 1:
        print(f"Extra string after the commands are ignored. {tokens[1:]} are ignored. ")
    App = Appointment(patient_instance=CURRENT_PATIENT, caregiver_instance=CURRENT_CAREGIVER)
    if CURRENT_CAREGIVER is None:
        try:
            Results = App.show_appointments_patient()
            print("Appointment ID  | Caregiver Name  | Date  | Vaccine")
            for row in Results:
                print(f"{row['id']}  | {row['CareGiverName']}  | {row['AppointmentDate']}  | {row['VaccineType']}")
            return None
        except pymssql.Error as sqle:
            warn("A database error occurred while trying to show list of appointment for a patient. ", sqle)
            quit()
            return None
        except Exception as e:
            warn("A non database error as occured while trying to show a list of appointment for a patient. ", e)
            return None
    else:
        try:
            Results = App.show_appointments_caregiver()
            print("Appointment ID  | Patient Name  | Date   | Vaccine")
            for row in Results:
                print(f"{row['id']}  | {row['PatientName']}  | {row['AppointmentDate']}  | {row['VaccineType']}")
        except pymssql.Error as sqle:
            warn("A database error occurred while trying to show list of appointment for a caregiver. ", sqle)
            quit()
            return None
        except Exception as e:
            warn("A non database error as occurred while trying to show a list of appointment for a caregiver. ", e)
            return None
    return None


def logout(tokens):
    """
        TODO: Part 2
    """

    global CURRENT_CAREGIVER, CURRENT_PATIENT
    if not (CURRENT_PATIENT is None and CURRENT_CAREGIVER is None):
        print(f"Logging out: {CURRENT_CAREGIVER}")
        print(f"Logging out: {CURRENT_PATIENT}")
        CURRENT_PATIENT = None
        CURRENT_CAREGIVER = None
    else:
        print("No account is currently login, so logout does nothing. ")

    return None


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # DONE: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  # DONE: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  # DONE: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>") # DONE: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>") # TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  # TODO: implement show_appointments (Part 2)
        print("> logout") # DONE: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        tokens = response.split(" ")
        tokens[0] = tokens[0].lower()

        if len(tokens) == 0:
            ValueError("Try Again")
            continue

        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


def Test():
    print("--- Test Creating Caregiver --- ")
    print("Inserting a new care giver to the system. ")
    create_caregiver(["", "test", "test"])
    return


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''
    # start command line
    Test()
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")
    start()
