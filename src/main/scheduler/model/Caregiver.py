import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Caregiver:

    def __init__(self, username, password=None, salt=None, hash=None):
        """
            Create a caregiver instance for the current login.
            Overview:
                * Pass in the salt and hash when it's made to create an instance of caregiver in the
                DB.
                * Pass in the password if it's an login attempt of an existing caregiver in the database.

        """
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    def get(self):
        """
            Login the caregiver account.
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            print("Error occurred when fetching current caregiver")
            raise e
        finally:
            cm.close_connection()
        return None

    def get_username(self):
        return self.username

    @property
    def Username(self):
        return self.get_username()

    def get_salt(self):
        return self.salt

    @property
    def Salt(self):
        return self.get_salt()

    def get_hash(self):
        return self.hash

    @property
    def Hash(self):
        return self.get_hash()

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    def upload_availability(self, d):
        """
            Insert availability for the caregiver who is currently logged in.
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
        try:
            cursor.execute(add_availability, (d, self.username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()

    def __repr__(self):
        """
            print out an representation of the current instance for the caregiver.
        """
        return f"instance type: Caregiver, usename: {self.username}"