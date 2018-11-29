import pyodbc
import socket
import time
import os
from datetime import datetime
from constants import values


def connect_database():
    try:
        cnxn = pyodbc.connect(values.connection_string)
        print("Database Connection Successfull")
        return cnxn
    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        print("ERROR_DATABASE_CONNECTION: ", sqlstate)
        return False


def write_to_file(data_decoded, timestamp):
    print("Writing data to file because connection failed.")

    fName = "connection_failed_backlog.txt"
    if os.path.exists(fName):
        with open(fName, 'a') as f:
            try:
                f.write(data_decoded + "," + timestamp + '\n')
                f.close()
            except:
                print("Error writting to file.")
    else:
        f = open(fName, 'a')
        f.write(data_decoded + "," + timestamp + '\n')
        f.close()

    print("Data logged in file connection_failed_backlog.txt")


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

        data_decoded = data.decode("UTF-8")
        event_type, id_room = (data_decoded.split(","))
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        print('\nRECIEVED: ', data.decode("UTF-8"), '  at  ', datetime.now())
        connection = connect_database()

        if connection == False:
            write_to_file(data_decoded, timestamp)
        else:
            cursor = connection.cursor()

            add_event = "INSERT INTO TBL_Eventos" \
                        " VALUES (%s, '%s', %s)" % (event_type, timestamp, id_room)

            cursor.execute(add_event)  # Insert new event

            connection.commit()
            print("Data added successfully.")
            print()
            cursor.close()
            connection.close()

    server.close()
