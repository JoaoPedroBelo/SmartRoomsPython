import pypyodbc
import socket
import time
from datetime import datetime


connection_string = "Driver={SQL Server Native Client 11.0};" \
                    "Server=smartroomsdbserver.database.windows.net;" \
                    "Database=smartrooms_db;" \
                    "uid=smartrooms;" \
                    "pwd=SDgrupo3_projecto"


def connect_database():
    try:
        cnxn = pypyodbc.connect(connection_string)
        print("Database Connection Successfull")
        return cnxn
    except pypyodbc.Error as ex:
        sqlstate = ex.args[1]
        print("ERROR_DATABASE_CONNECTION: ", sqlstate)
        return False


if __name__ == "__main__":
    server_address = ('localhost', 6789)
    max_size = 4096

    print('Starting the server at', datetime.now())

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(server_address)

    while True:  # making a loop
        print('Waiting for sensors.')
        data, client = server.recvfrom(max_size)

        if data == b'stop':
            print("Stopping server.")
            break

        print('At', datetime.now(), client, 'said', data)
        server.sendto(b'Data recieved', client)

    server.close()


    # cursor = cnx.cursor()
    #
    # timestamp = datetime.now()
    # event_type = 0
    # id_room = 1
    #
    # add_event = ("INSERT INTO TBL_Eventos "
    #                "(tipo, time, TBL_Salas_id) "
    #                "VALUES (%s, %s, %s)")
    #
    # data_event = (event_type, timestamp, id_room)
    #
    # # Insert new employee
    # cursor.execute(add_event, data_event)
    # # emp_no = cursor.lastrowid
    #
    # # Make sure data is committed to the database
    # cnx.commit()
    #
    # cursor.close()
    # cnx.close()

