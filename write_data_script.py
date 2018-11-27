import pyodbc
import socket
import time
from datetime import datetime


connection_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=smartroomsdbserver.database.windows.net;;DATABASE=smartrooms_db;UID=smartrooms;PWD=SDgrupo3_projecto"


def connect_database():
    try:
        cnxn = pyodbc.connect(connection_string)
        print("Database Connection Successfull")
        return cnxn
    except pyodbc.Error as ex:
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
        server.sendto(b'Data recieved', client)

        if data == b'stop':
           print("Stopping server.")
           break

        print('RECIEVED: ', data.decode("UTF-8"), '  at  ', datetime.now())
        connection = connect_database()
        cursor = connection.cursor()

        event_type, id_room = (data.decode("UTF-8")).split(",")
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        add_event = "INSERT INTO TBL_Eventos" \
                    " VALUES (%s, '%s', %s)" % (event_type, timestamp, id_room)

        cursor.execute(add_event)  # Insert new event

        connection.commit()
        print("Data added successfully.")
        print()
        cursor.close()
        connection.close()

    server.close()

    # # RETURN ALL EVENT TABLE ROWS
    # connection = connect_database()
    # cursor = connection.cursor()
    #
    # cursor.execute('SELECT * FROM TBL_Eventos')
    # print('')
    #
    # for row in cursor.fetchall():
    #     for field in row:
    #         print(field)
    #     print('')
    #
    # connection.commit()
    # cursor.close()
    # connection.close()
