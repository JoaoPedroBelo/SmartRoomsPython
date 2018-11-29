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


def write_to_file(par_data_decoded, par_timestamp):
    print("Writing data to file because connection failed.")

    fname = "connection_failed_backlog.txt"
    if os.path.exists(fname):
        with open(fname, 'a') as f:
            try:
                f.write(par_data_decoded + ";" + par_timestamp + '\n')
                f.close()
            except Exception as e:
                print("ERROR WRITTING FILE: " + str(e))
                return
    else:
        f = open(fname, 'a')
        f.write(par_data_decoded + ";" + par_timestamp + '\n')
        f.close()

    print("Data logged in file connection_failed_backlog.txt")


def insert_event_into_database(par_connection, par_event_type, par_timestamp, par_id_room):
    add_event = "INSERT INTO TBL_Eventos" \
                " VALUES (%s, '%s', %s)" % (par_event_type, par_timestamp, par_id_room)

    try:
        cursor = par_connection.cursor()
        cursor.execute(add_event)  # Insert new event
        par_connection.commit()
    except Exception as e:
        print("ERROR INSERTING INTO DB: " + str(e))
        write_to_file(par_event_type + ',' + id_room, par_timestamp)
        return

    print("Data added successfully." + '\n')
    cursor.close()
    par_connection.close()


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

        print('\nRECIEVED: ', data_decoded, '  at  ', datetime.now())

        connection = connect_database()

        if connection is False:
            write_to_file(data_decoded, timestamp)
        else:

            insert_event_into_database(connection, event_type, timestamp, id_room)


    server.close()
