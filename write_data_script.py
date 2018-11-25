import pypyodbc
import socket
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
        server.sendto(b'Data recieved', client)

        if data == b'stop':
           print("Stopping server.")
           break

        # print('RECIEVED: ', data, '  at  ', datetime.now())
        connection = connect_database()
        cursor = connection.cursor()

        # cursor.execute('''SELECT * FROM TBL_Eventos;''')
        # cursor.commit()
        #
        # for d in cursor.description:
        #     print(d[0])
        #
        # print('')
        #
        # for row in cursor.fetchall():
        #     for field in row:
        #         print(field)
        #     print('')

        # INSERIR EVENTO RECEBIDO

        event_type, id_room = (data.decode("UTF-8")).split(",")
        timestamp = datetime.now()

        add_event = "INSERT INTO TBL_Eventos" \
                    " VALUES (%s, %s, %s)"

        data_event = [(event_type, timestamp, id_room)]

        cursor.execute(add_event, data_event)  # Insert new event

        connection.commit()
        cursor.close()
        connection.close()

    server.close()
