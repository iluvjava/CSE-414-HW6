from db.ConnectionManager import ConnectionManager

def main():
    cm = ConnectionManager()
    SQL = "SELECT TOP 1 Username FROM Availabilities WHERE Time = %s ORDER BY RAND()"
    with cm as cursor:
        cursor.execute(SQL, ("2022-02-22", ))
        for row in cursor:
            print(row)

main()