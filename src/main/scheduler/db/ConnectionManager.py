import pymssql
import os
import warnings

class ConnectionManager:

    def __init__(self):
        self.server_name = os.getenv("SERVER")
        self.db_name = os.getenv("DBNAME")
        self.user = os.getenv("USERID")
        self.password = os.getenv("PASSWORD")
        self.conn = None

    def create_connection(self):
        """
            Get a SQL connection object, which is commonly refers to as the cursor.
            Exception:
                * Exists the program whenever a database connection error is encountered.
        """
        try:
            if self.server_name is None:
                warnings.warn("SERVER Env Var is None.")
            if self.db_name is None:
                warnings.warn("DBNAME Env Var is None.")
            if self.user is None:
                warnings.warn("USERID Env Var is None.")
            if self.password is None:
                warnings.warn("PASSWORD Env Var is None.")
            self.conn = pymssql.connect(
                server=self.server_name,
                user=self.user,
                password=self.password,
                database=self.db_name
            )
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            print(db_err)
            quit()
        return self.conn

    def close_connection(self):
        """
            Close the current database connection session.
            Exception:
                * It will quit the program if there is a database connection error.
        """
        try:
            self.conn.close()
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            print(db_err)
            quit()
