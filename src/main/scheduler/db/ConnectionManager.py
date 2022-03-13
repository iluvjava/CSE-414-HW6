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

    def create_connection(self, autocommit=False):
        """
            Get a SQL connection object, which is commonly refers to as the cursor.
            Exception:
                * Exists the program whenever a database connection error is encountered.
        """
        try:
            AnyProblem = False
            if self.server_name is None:
                warnings.warn("SERVER Env Var is None.")
                AnyProblem = True
            if self.db_name is None:
                warnings.warn("DBNAME Env Var is None.")
                AnyProblem = True
            if self.user is None:
                warnings.warn("USERID Env Var is None.")
                AnyProblem = True
            if self.password is None:
                warnings.warn("PASSWORD Env Var is None.")
                AnyProblem = True
            if AnyProblem:
                print("Problems with environmental variables, please make sure they are all capitalized. I added this thing" + \
                      "so that it's compatible with my system, which is not original present in the original assignment code. ")

            self.conn = pymssql.connect(
                server=self.server_name,
                user=self.user,
                password=self.password,
                database=self.db_name,
                autocommit=autocommit
            )
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! The program will be terminated immediately.")
            print(db_err)
            quit()  # KILL the program if such an error occurred. Oof might not be a good move but whatever.
        return self.conn

    def __enter__(self):
        """
            Enter with Block. Directly get the cursor for MSSQL under the with
            context. It has auto commit.
            * Under the contex, the query results are in dictionary format, and
            auto-commit is enabled.
        """
        self.create_connection(autocommit=True)
        return self.conn.cursor(as_dict=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
            Close it when existing the with block.
            All errors and exceptions are the responsibility of the caller of the with context.
        """
        self.close_connection()
        return False

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
