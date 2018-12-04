import pyodbc
from constants import values
import os


def connect_database():
    try:
        cnxn = pyodbc.connect(values.connection_string)
        print("Database Connection Successfull")
        return cnxn
    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        print("ERROR_DATABASE_CONNECTION: ", sqlstate)
        return False


def check_room_occupation(par_cursor, par_id_room):
    # check room occupation in DB
    try:
        par_cursor.execute("SELECT SUM(tipo) FROM TBL_Eventos WHERE TBL_Salas_id = " + str(par_id_room))
    except pyodbc.Error as e:
        print("ERROR GETTING ROOM OCCUPATION: " + str(e))

    for row in cursor.fetchall():
        room_ocupation = row[0]

    # check room occupation in backlog
    fname = "connection_failed_backlog.txt"
    content = []
    if os.path.exists(fname):  # reads entire file and saves it in content
        with open(fname) as f:
            try:
                content = f.readlines()
                content = [x.strip() for x in content]
                f.close()
            except Exception as e:
                print("ERROR READING FILE: " + str(e))
                return

    for line in content:
        s_event_type, s_id_room, s_timestamp = line.split(',')

        if int(s_id_room) == par_id_room:
            room_ocupation += int(s_event_type)

    return room_ocupation


connection = connect_database()

if connection:
    cursor = connection.cursor()
    for i in range(4):
        print("OCCUPATION - Room " + str(i) + ": " + str(check_room_occupation(cursor, i)))
else:
    print("Failed due to connection")

connection.close()
