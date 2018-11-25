import mysql.connector
from mysql.connector import errorcode
import time
from datetime import datetime


database_config = {
    'user': 'smartrooms@smartrooms',
    'password': 'SDgrupo3_projet',
    'host': 'smartrooms.mariadb.database.azure.com',
    'database': 'mydb',
    'port': 3306,
    'raise_on_warnings': True
}


def connect_database():
    try:
        cnx = mysql.connector.connect(**database_config)
        print("Database Connection Successfull")
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

        return False


if __name__ == "__main__":
    print(connect_database())
    #

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

