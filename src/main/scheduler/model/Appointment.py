import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import datetime


class Appointment:
    """
        An appointment object that models the appointment between a patient, caregiver, and vaccine
        at certain date.

    """
    VaccineExists = "SELECT COUNT(*) AS C FROM Vaccines WHERE Name = %s"
    CareGiverScheduleExists = "SELECT COUNT(*) AS C FROM Availabilities WHERE Time = %s"
    InsertAppointment = "INSERT INTO Appointments VALUES(%s, %s, %s, %s)"
    GetRandomCaregiver = "SELECT TOP 1 Username FROM Availabilities WHERE Time = %s ORDER BY RAND()"

    def __init__(self, vaccine:str, date:str, appointment_id=None, patient_instance=None, caregiver_instance=None):
        """
            models all some specific appointment.
        """
        self.patient_instance = patient_instance
        self.caregiver_instance = caregiver_instance
        self.patient_name = patient_instance.UserName if patient_instance is not None else None
        self.caregiver_name = caregiver_instance.UserName if caregiver_instance is not None else None
        self.date = date
        self.appointment_id = appointment_id
        self.vaccine = vaccine
        self.is_validated = False
        return None

    @property
    def PatientInstance(self):
        return self.patient_instance

    @property
    def AppointmentDate(self):
        return self.date

    @property
    def AppointmentID(self):
        return self.appointment_id

    def validate_appointment(self):
        """
            Checks the appointment for the patience.
            None will be returned if appointment it's successfully validated. If there is something
            wrong while validating the given appointment, Error messages will be returned to the caller for
            processing.
            * no need to validate user because it already exists in the database.
            * validate vaccine to see if it's actually there.
            * validate date and check if it's legit.
            * validate if the date is in the future.
            * validate if any caregiver is available at the given date.
            Exceptions:
                Handle by the caller.
        """
        if self.appointment_id is not None:
            # this is already a validated appointment if this field exists.
            return None
        if self.patient_instance is None:
            return "Can't validate appointment for a patience on behave of a caregiver. "
        # ----- Validate date ----------
        if not Util.CheckDateCorrect(self.date):
            return f"The date is incorrect. The date given is: \"{self.date}\""
        TodayDate = datetime.date.today()
        TodayDateTime = datetime.datetime.combine(TodayDate, datetime.datetime.min.time())
        AppointmentDate = datetime.datetime.strptime(self.AppointmentDate, "%Y-%m-%d")
        if AppointmentDate < TodayDateTime:
            return f"The appointment date comes before today's day. " + \
                  f"Appointment date is: {AppointmentDate.strftime('%Y-%m-%d')}" + \
                  f" Today's date is: {TodayDateTime.strftime('%Y-%m-%d')}"

        # ------ validate vaccine, care giver -----
        cm = ConnectionManager()
        with cm as cursor:
            cursor.execute(Appointment.VaccineExists, (self.vaccine, ))
            Flag = None
            for row in cursor:
                # vaccine exists.
                Flag = row["C"]
            if Flag != 1:
                return f"Vaccine: \"{self.vaccine}\" doesn't exist in the database."
            cursor.execute(Appointment.CareGiverScheduleExists, (self.date, ))
            Flag = None
            for row in cursor:
                # caregiver exists
                Flag = row["C"]
            if Flag < 1:
                return f"Current, No caregiver is available for the date: {self.date} " + \
                        "try another date please. "
        self.is_validated = True
        return None

    def add_appointment(self):
        """
            Always validate the appointment before adding it.
            Exceptions:
                The caller's responsibility.
        """
        if not self.is_validated:
            raise Exception("Can't add appointment to database when it's not validated yet. ")
        if self.patient_instance is None:
            raise Exception("The appointment must be made for patience to be added to the database. ")
        cm = ConnectionManager()

        with cm as cursor:
            cursor.execute(Appointment.GetRandomCaregiver, (self.date, ))
            CareGiverName = None
            for row in cursor:
                CareGiverName = row["Username"]
            cursor.execute(Appointment.InsertAppointment, (self.patient_name, CareGiverName, self.date, self.vaccine))
        return None

    def show_appointments_patient(self):
        """
            Returns the query results for an instance of patient. The results will be returned as a list of
            dictionary.
        """
        return None


    def show_appointment_caregiver(self):
        """
            Returns the query results for an instance of caregiver. The results will be returned as a list
            of dictionary.

        """

        return None







