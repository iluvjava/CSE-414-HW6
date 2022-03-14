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
        if date_string is None:
            return False
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
    def CheckIfGoodPassword(password:str):
        """
            Given a string, function checks whether the password satisfy the following standard:
            1. At least 8 characters.
            2. A mixture of both uppercase and lowercase letters.
            3. A mixture of letters and numbers.
            4. Inclusion of at least one special character, from “!”, “@”, “#”, “?”.
            Returns:
                None if everything is good. A message if any of the password criteria is not satisfied.
        """
        if len(password) < 8:
            return "Password Length should be at least 8 characters long."
        # password is at least 8 letter long
        if all([ord('a') > ord(l) > ord('z') for l in password.lower()]):
            return "Password should at least contain some letters in it. "
        # password is at least 8 letters long and contain at least one letter
        if password.upper() == password or password.lower() == password:
            return "Password must contain a mixture of both upper and lower case letter. "
        # password is at least 8 letters long and contain at least one upper and lower case letter
        if len(set("1234567890").intersection(set(password))) == 0:
            return "Password must contain a mixture of both letters and numbers"
        # password is at least 8 letters long and contain at least one upper and lower case letter and some digits.
        if len(set("!@#?").intersection(set(password))) == 0:
            return "Password must include at least one of the characters from “!”, “@”, “#”, “?”. "
        return None
