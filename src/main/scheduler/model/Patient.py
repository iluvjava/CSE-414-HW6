import sys
import warnings

sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Patient:

    GetPatientDetails = "SELECT Salt, Hash FROM Patients WHERE Username = %s"
    PatientExists = "SELECT * FROM Patients WHERE Username = %s"
    AddPatient = "INSERT INTO Patients VALUES(%s, %s, %s)"

    def __init__(self, username, password=None, salt=None, hash=None):
        """
            Load in an instance of the Patient, completed with username password salt and hash.
            * When creating a new user, pass in the salt and hash.
            * when logging in existing user, pass in the password only.
        """
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash
        return

    def __call__(self):
        return self.get()

    def get(self):
        """
            Makes connection to the database for the current user info.
            Exceptions:
                Database: pymssql.Error
            None:
                When the patient doesn't exist in the database.
                Incorrect password.
        """
        cm = ConnectionManager()
        if not self.exists_in_db():
            warnings.warn("patient doesn't exists in database but caller insists on getting it from database. ")
            print("None is returned. ")
            return None
        with cm as cursor:
            cursor.execute(Patient.GetPatientDetails, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                # password wrong.
                if not curr_hash == calculated_hash:
                    print("Incorrect password")
                    return None
                else:
                    # establish salt and hash from the db.
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    return self
        return None


    def exists_in_db(self):
        """
            Check if the current establish instance of the logged in patient exists in the database we had.
            Exception and Error:
                It's the caller's responsiblity for handling exceptions from the database operations.
        """
        cm = ConnectionManager()
        with cm as cursor:
            cursor.execute(Patient.PatientExists, self.username)
            for row in cursor:
                return row["Username"] is not None
        return None

    def get_username(self):
        return self.username

    @property
    def UserName(self):
        return self.get_username()

    def get_salt(self):
        return self.salt

    @property
    def Salt(self):
        return self.get_salt()

    @Salt.setter
    def Salt(self, value):
        self.salt=value

    def get_hash(self):
        return self.hash

    @property
    def Hash(self):
        return self.get_hash()

    @Hash.setter
    def Hash(self, value):
        self.hash = value

    def save_to_db(self):
        """
            Save the current instance of patient into the table.
            Exception:
                It might give database exceptions, this is the caller's responsibility.
                pymssql.Error
        """
        cm = ConnectionManager()
        if self.hash is None or self.salt is None:
            raise AssertionError("Unable to save patient database object because one of the salt or hash field is None.")
        with cm as cursor:
            cursor.execute(Patient.AddPatient, (self.username, self.salt, self.hash))
            # auto commit.
        return True

    def __repr__(self):
        """
            Get representation for the instance.
        """
        return f"type: Patient, username: {self.username}"



