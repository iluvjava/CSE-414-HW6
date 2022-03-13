import re

from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import warnings
import traceback


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
CURRENT_PATIENT = None
CURRENT_CAREGIVER = None

CONST_SELECT_CAREGIVER_USERNAME = "SELECT * FROM Caregivers WHERE Username = %s"
CONST_GET_ALL_VACCINE = "SELECT * FROM Vaccines"
CONST_SELECT_CAREGIVER_AVAILABLE_FOR_DATE = "SELECT * FROM Availabilities WHERE time = %s"


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
        print(dbe)
        warnings.warn("Unable to save created patient to the database. ")
        return None
    except Exception as e:
        traceback.print_exc()
        warnings.warn("Exception occurred while saving the account created. ")
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
        print("Create caregiver failed, Cannot save")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error:", e)
        return
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
    except Exception as e:
        print("Error:", e)
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
            print(f"Can't login because {CURRENT_PATIENT} is currently logged in. ")
        else:
            print(f"Can't login because {CURRENT_CAREGIVER} is currently logged in. ")
        return None
    if len(tokens) != 3:
        print(f"Tokenization failed, expect 3 tokens from the command input, but gotten: \n{tokens}")
    username, password = tokens[1], tokens[2]
    try:   # try logging in and store the session for the login.
        ThePatient = Patient(username, password=password).get()
        print(f"Current login patient: {username}")
        CURRENT_PATIENT = ThePatient
    except pymssql.Error as e:
        traceback.print_exc()
        print("An database error occured when trying to login the patient. ")
        return None
    except Exception as e:
        traceback.print_exc()
        print("Another non database error has occured while processing the login of the patient. ")
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
    # TODO: Implement this.
    if len(tokens) != 2:
        print(f"Tokenization failed, except 2 tokens but we got: {tokens}")
        return None
    date = tokens[1]
    if re.findall(r"^\d{4}-\d{2}-\d{2}", date) != 1:
        print("Don't give that, date of in the formate of YYYY-MM-DD")
        return None
    if CURRENT_CAREGIVER is None and CURRENT_PATIENT is None:
        print("You haven't login, please login to retrieve schedule info. ")
        return None


    pass


def reserve(tokens):
    """
        TODO: Part 2
    """

    pass


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
    '''
        TODO: Part 2
    '''
    pass


def logout(tokens):
    """
        TODO: Part 2
    """
    global CURRENT_CAREGIVER, CURRENT_PATIENT
    print(f"Logging ou: {CURRENT_CAREGIVER}")
    print()

    return


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  # TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  # TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>") # TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>") # TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  # TODO: implement show_appointments (Part 2)
        print("> logout") # TODO: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        response = response.lower()
        tokens = response.split(" ")
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
