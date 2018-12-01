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
                f.write(par_data_decoded + "," + par_timestamp + '\n')
                f.close()
            except Exception as e:
                print("ERROR WRITTING FILE: " + str(e))
                return False
    else:
        f = open(fname, 'a')
        f.write(par_data_decoded + "," + par_timestamp + '\n')
        f.close()

    print("Data logged in file connection_failed_backlog.txt" + '\n')
    return True


def insert_event_into_database(par_connection, par_event_type, par_timestamp, par_id_room):
    add_event = "INSERT INTO TBL_Eventos" \
                " VALUES (%s, '%s', %s)" % (par_event_type, par_timestamp, par_id_room)

    cursor = par_connection.cursor()
    cursor.execute("SELECT SUM(tipo) FROM TBL_Eventos WHERE TBL_Salas_id = " + str(par_id_room))

    for row in cursor.fetchall():
        room_ocupation = row[0]

    if room_ocupation > 0 or par_event_type == 1:  # if room is empty doesnt insert an exited room event
        try:
            cursor.execute(add_event)  # Insert new event if room isnt empty
            par_connection.commit()
        except Exception as e:
            print("ERROR INSERTING INTO DB: " + str(e))
            write_to_file(par_event_type + ',' + par_id_room, par_timestamp)
            return False
    else:
        print("ERROR INSERTING EVENT: Room " + par_id_room + " is empty" + '\n')
        return False

    print("Data added successfully." + '\n')
    cursor.close()
    par_connection.close()
    return True


def retry_inserting_backlog():
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

    with open(fname, 'w') as f:
        try:
            while content:
                line = content[0]
                event_type, id_room, timestamp = line.split(',')
                connection = connect_database()
                if connection is False:
                    break
                else:
                    result = insert_event_into_database(connection, int(event_type), timestamp, id_room)

                if result:
                    content.pop(0)

        except Exception as e:
            print("ERROR in retry_inserting_backlog: " + str(e) + '\n')
            for line in content:
                f.write(line + '\n')

            return False

        while content:
            line = content.pop(0)
            f.write(line + '\n')

        f.close()


if __name__ == "__main__":
    retry_inserting_backlog()
    # server_address = ('localhost', 6789)
    # max_size = 4096
    #
    # print('Starting the server at', datetime.now())
    #
    # server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # server.bind(server_address)
    #
    # while True:  # making a loop
    #     print('Waiting for sensors.')
    #     data, client = server.recvfrom(max_size)
    #     server.sendto(b'Data recieved', client)
    #
    #     if data == b'stop':
    #         print("Stopping server.")
    #         break
    #
    #     data_decoded = data.decode("UTF-8")
    #     event_type, id_room = (data_decoded.split(","))
    #     timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    #
    #     print('\nRECIEVED: ', data_decoded, '  at  ', datetime.now())
    #
    #     connection = connect_database()
    #
    #     if connection is False:
    #         write_to_file(data_decoded, timestamp)
    #     else:
    #         insert_event_into_database(connection, event_type, timestamp, id_room)
    #
    # server.close()
