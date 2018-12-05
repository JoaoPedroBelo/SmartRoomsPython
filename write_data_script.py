import pyodbc
import socket
import time
import os
from datetime import datetime
from constants import values
# para o raspberry
# import logging
# alterar todos os prints para logging.info
# adicionar no inicio logging.basicConfig(filename='/home/pi/projeto/write_data_script.log',level=logging.DEBUG)


def connect_database():
    try:
        cnxn = pyodbc.connect(values.connection_string)
        print(str(datetime.now()) + ': ' + "Database Connection Successfull")
        return cnxn
    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        print(str(datetime.now()) + ': ' + "ERROR_DATABASE_CONNECTION: " + sqlstate)
        return False


def insert_event_into_database(par_connection, par_cursor, par_event_type, par_timestamp, par_id_room):
    add_event = "INSERT INTO TBL_Eventos" \
                " VALUES (%s, '%s', %s)" % (par_event_type, par_timestamp, par_id_room)

    room_ocupation = check_room_occupation(par_cursor, par_id_room)

    if room_ocupation > 0 or par_event_type == 1:  # if room is empty doesnt insert an exited room event
        try:
            par_cursor.execute(add_event)  # Insert new event if room isnt empty
            par_connection.commit()
        except pyodbc.Error as e:
            print(str(datetime.now()) + ': ' + "ERROR INSERTING INTO DB: " + str(e))
            write_to_file(str(par_event_type) + ',' + str(par_id_room), par_timestamp)
            return False
    else:
        print(
            str(datetime.now()) + ': ' + "ERROR INSERTING EVENT: Room " + str(par_id_room) + " is empty" + '\n')
        return False

    print(str(datetime.now()) + ': ' + "Data added successfully." + '\n')
    return True


def check_room_occupation(par_cursor, par_id_room):
    # check room occupation in DB
    try:
        par_cursor.execute("SELECT SUM(tipo) FROM TBL_Eventos WHERE TBL_Salas_id = " + str(par_id_room))
    except pyodbc.Error as e:
        print(str(datetime.now()) + ': ' + "ERROR GETTING ROOM OCCUPATION: " + str(e))

    for row in cursor.fetchall():
        room_ocupation = row[0]

    # check room occupation in backlog
    fname = "/home/pi/projeto/connection_failed_backlog.txt"
    content = []
    if os.path.exists(fname):  # reads entire file and saves it in content
        with open(fname) as f:
            try:
                content = f.readlines()
                content = [x.strip() for x in content]
                f.close()
            except Exception as e:
                print(str(datetime.now()) + ': ' + "ERROR READING FILE: " + str(e))
                return

    for line in content:
        s_event_type, s_id_room, s_timestamp = line.split(',')

        if int(s_id_room) == par_id_room:
            room_ocupation += int(s_event_type)

    return room_ocupation


def write_to_file(par_data_decoded, par_timestamp):
    print(str(datetime.now()) + ': ' + "Writing data to file because connection failed.")

    fname = "/home/pi/projeto/connection_failed_backlog.txt"
    if os.path.exists(fname):
        with open(fname, 'a') as f:
            try:
                f.write(par_data_decoded + "," + par_timestamp + '\n')
                f.close()
            except Exception as e:
                print(str(datetime.now()) + ': ' + "ERROR WRITTING FILE: " + str(e))
                return False
    else:
        f = open(fname, 'a')
        f.write(par_data_decoded + "," + par_timestamp + '\n')
        f.close()

    print(str(datetime.now()) + ': ' + "Data logged in file connection_failed_backlog.txt" + '\n')
    return True


def retry_inserting_backlog(par_connection, par_cursor):
    fname = "/home/pi/projeto/connection_failed_backlog.txt"
    content = []
    if os.path.exists(fname):  # reads entire file and saves it in content
        with open(fname) as f:
            try:
                content = f.readlines()
                content = [x.strip() for x in content]
                f.close()
            except Exception as e:
                print(str(datetime.now()) + ': ' + "ERROR READING FILE: " + str(e))
                return

    with open(fname, 'w') as f:
        try:
            while content:
                print(str(datetime.now()) + ': ' + '\n\nTrying to insert the backlog into the DB:\n')
                line = content[0]
                s_event_type, s_id_room, s_timestamp = line.split(',')
                result = insert_event_into_database(par_connection, par_cursor, int(s_event_type), s_timestamp,
                                                    s_id_room)

                if result:
                    content.pop(0)

                else:
                    break

        except Exception as e:
            print(str(datetime.now()) + ': ' + "ERROR in retry_inserting_backlog: " + str(e) + '\n')
            for line in content:
                f.write(line + '\n')

        f.close()


if __name__ == "__main__":
    server_address = ('localhost', 6789)
    max_size = 4096

    print(str(datetime.now()) + ': ' + 'Starting the server.')

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(server_address)

    while True:  # making a loop
        print(str(datetime.now()) + ': ' + 'Waiting for sensors.')
        data, client = server.recvfrom(max_size)
        server.sendto(b'Data recieved', client)

        data_decoded = data.decode("UTF-8")
        event_type, id_room = (data_decoded.split(","))
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        print(str(datetime.now()) + ': ' + '\nRECIEVED: ' + data_decoded)

        connection = connect_database()

        if connection is False:
            write_to_file(data_decoded, timestamp)
        else:
            cursor = connection.cursor()

            retry_inserting_backlog(connection, cursor)

            insert_event_into_database(connection, cursor, int(event_type), timestamp, id_room)

        cursor.close()
        connection.close()

    # server.close()
