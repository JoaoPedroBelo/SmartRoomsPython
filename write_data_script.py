import pyodbc
import socket
import time
import os
from datetime import datetime
from constants import values, functions
import logging

##
def connect_database():
    try:
        cnxn = pyodbc.connect(values.connection_string)
        functions.message(str(datetime.now()) + ': ' + "Database Connection Successfull")
        return cnxn
    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        functions.message(str(datetime.now()) + ': ' + "ERROR_DATABASE_CONNECTION: " + sqlstate)
        return False


def insert_event_into_database(par_connection, par_cursor, par_event_type, par_timestamp, par_id_room,
                               par_occupied_seats, par_empty_seats):
    add_event = ("INSERT INTO TBL_Eventos VALUES (%s, '%s', %s, %s, %s)"
                 % (par_event_type, par_timestamp, par_id_room, par_occupied_seats, par_empty_seats))

    try:
        par_cursor.execute(add_event)  # Insert new event if room isnt empty
        par_connection.commit()
    except pyodbc.Error as e:
        functions.message(str(datetime.now()) + ': ' + "ERROR INSERTING INTO DB: " + str(e))
        write_to_file(str(par_event_type) + ',' + str(par_id_room) + "," + par_timestamp + ','
                      + par_occupied_seats + ',' + par_empty_seats)
        return False

    functions.message(str(datetime.now()) + ': ' + "Data added successfully." + '\n')
    return True


def check_room_occupation(par_cursor, par_id_room):
    # check room occupation in DB
    try:
        par_cursor.execute("SELECT TOP 1 * FROM TBL_Eventos WHERE TBL_Salas_id = %s ORDER BY time DESC"
                           % str(par_id_room))
    except pyodbc.Error as e:
        functions.message(str(datetime.now()) + ': ' + "ERROR GETTING ROOM OCCUPATION: " + str(e))

    for row in par_cursor.fetchall():
        room_ocupation = int(row[4])

    # check room occupation in backlog
    fname = values.file_name
    content = []
    if os.path.exists(fname):  # reads entire file and saves it in content
        with open(fname) as f:
            try:
                content = f.readlines()
                content = [x.strip() for x in content]
                f.close()
            except Exception as e:
                functions.message(str(datetime.now()) + ': ' + "ERROR READING FILE: " + str(e))
                return

    for line in content:
        s_event_type, s_id_room, s_timestamp, s_occupied_seats, s_empty_seats = line.split(',')

        if int(s_id_room) == par_id_room:
            room_ocupation += int(s_event_type)

    return room_ocupation


def write_to_file(par_data):
    functions.message(str(datetime.now()) + ': ' + "Writing data to file because connection failed.")

    fname = values.file_name
    if os.path.exists(fname):
        with open(fname, 'a') as f:
            try:
                f.write(par_data + '\n')
                f.close()
            except Exception as e:
                functions.message(str(datetime.now()) + ': ' + "ERROR WRITTING FILE: " + str(e))
                return False
    else:
        f = open(fname, 'a')
        f.write(par_data + '\n')
        f.close()

    functions.message(str(datetime.now()) + ': ' + "Data logged in file connection_failed_backlog.txt" + '\n')
    return True


def retry_inserting_backlog(par_connection, par_cursor):
    fname = values.file_name
    content = []
    if os.path.exists(fname):  # reads entire file and saves it in content
        with open(fname) as f:
            try:
                content = f.readlines()
                content = [x.strip() for x in content]
                f.close()
            except Exception as e:
                functions.message(str(datetime.now()) + ': ' + "ERROR READING FILE: " + str(e))
                return

    while content:
        functions.message(str(datetime.now()) + ': ' + '\n\nTrying to insert the backlog into the DB:\n')
        line = content[0]
        s_event_type, s_id_room, s_timestamp, s_occupied_seats, s_empty_seats = line.split(',')
        result = insert_event_into_database(par_connection, par_cursor, int(s_event_type), s_timestamp,
                                            s_id_room, s_occupied_seats, s_empty_seats)

        if result:
            content.pop(0)
        else:
            break

    with open(fname, 'w') as f:
        for line in content:
            f.write(line + '\n')

        f.close()


def get_room_capacity(par_cursor):
    room_capacity = [0, 0, 0, 0]

    try:
        par_cursor.execute("SELECT * FROM TBL_Salas")
        data = par_cursor.fetchall()
        for row in data:
            room_capacity[row[0]] = row[2]
    except pyodbc.Error as e:
        functions.message(str(datetime.now()) + ': ' + "ERROR getting room capacity from DB: " + str(e))
        return False

    return room_capacity


if __name__ == "__main__":
    server_address = ('localhost', 6789)
    max_size = 4096

    functions.start_logging('/home/pi/projeto/write_data_script.log')
    functions.message(str(datetime.now()) + ': ' + 'Starting the server.')

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(server_address)

    connection = connect_database()
    cursor = connection.cursor()

    occupied_seats = [0, 0, 0, 0]
    room_capacity = get_room_capacity(cursor)
    empty_seats = room_capacity
    for i in range(4):
        room_i_occupation = check_room_occupation(cursor, i)
        occupied_seats[i] += room_i_occupation
        empty_seats[i] -= room_i_occupation

    cursor.close()
    connection.close()

    while True:  # making a loop
        functions.message(str(datetime.now()) + ': ' + 'Waiting for sensors.')
        data, client = server.recvfrom(max_size)
        server.sendto(b'Data recieved', client)

        data_decoded = data.decode("UTF-8")
        event_type, id_room = (data_decoded.split(","))
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        id_room = int(id_room)
        event_type = int(event_type)

        functions.message(str(datetime.now()) + ': ' + '\nRECIEVED: ' + data_decoded)

        connection = connect_database()

        proceeds = True
        if event_type == -1 and occupied_seats[id_room] > 0:
            occupied_seats[id_room] -= 1
            empty_seats[id_room] += 1
        elif event_type == 1 and empty_seats[id_room] > 0:
            occupied_seats[id_room] += 1
            empty_seats[id_room] -= 1
        else:
            functions.message("Room %s is full/empty false entry/exit" % id_room)
            proceeds = False

        if proceeds:
            if connection is False:
                write_to_file(data_decoded + ',' + timestamp + ',' + str(occupied_seats[id_room])
                              + ',' + str(empty_seats[id_room]))
            else:
                cursor = connection.cursor()

                retry_inserting_backlog(connection, cursor)

                insert_event_into_database(connection, cursor, event_type, timestamp, id_room,
                                           occupied_seats[id_room], empty_seats[id_room])

        try: # tries to close the cursor if its still open
            cursor.close()
        except pyodbc.Error as e:
            pass
        connection.close()

    # server.close()
