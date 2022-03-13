import hashlib
import os
import datetime

class Util:

    @staticmethod  # added later.
    def generate_salt():
        return os.urandom(16)

    @staticmethod
    def generate_hash(password, salt):
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,
            dklen=16
        )
        return key

    @staticmethod
    def CheckDateCorrect(date_string):
        """
            Check if a current string is a correct date that can be parsed by the
            date time objective in python.
        """
        DateStringLst = date_string.split("-")
        if len(DateStringLst) != 3:
            return False
        Year, Month, Day = DateStringLst[0], DateStringLst[1], DateStringLst[2]
        Year, Month, Day = int(Year), int(Month), int(Day)
        try:
            _ = datetime.datetime(Year, Month, Day)
            return True
        except ValueError:
            return False
        # if other exception occurred here, then WTF I guess.
        return None

    @staticmethod
    def CheckDataIsThePast():
        """

        """
        pass