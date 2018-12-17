import os
from constants import functions, values
import logging
import pyodbc
import time
from datetime import datetime


def update_status(query):
    try:
        connection = pyodbc.connect(values.connection_string)
        cursor = connection.cursor()
        cursor.execute(query)  # Insert new event if room isnt empty
        connection.commit()
        cursor.close()
        connection.close()
        functions.message(str(datetime.now()) + ': ' + "SERVICES STATUS updated successfully." + '\n')
        return True
    except pyodbc.Error as e:
        functions.message(str(datetime.now()) + ': ' + "ERROR UPDATING SERVICES STATUS: " + str(e))
        return False


if __name__ == "__main__":
    functions.start_logging('/home/pi/projeto/service_monitoring.log')

    functions.message(str(datetime.now()) + ": Getting existing services from database")
    try:
        query = ("SELECT * FROM TBL_Services")
        connection = pyodbc.connect(values.connection_string)
        cursor = connection.cursor()

        all_services = cursor.execute(query).fetchall()
        print(all_services)
        services_status = []
        for row in all_services:
            services_status.append([row[0],row[2],'stopped'])

        cursor.close()
        connection.close()
    except Exception as e:
        functions.message(str(datetime.now()) + ': ' + "ERROR: " + str(e))

    # Update status every x seconds
    time_to_wait = 30
    while True:
        status_part = ""
        last_update_part = ""
        for i in range(len(services_status)):
            status = os.system('systemctl status ' + str(services_status[i][1]) + ' > /dev/null')
            if status == 0:
                services_status[i][2] = 'Ok'
            else:
                services_status[i][2] = 'Dead'

            status_part += " (" + str(services_status[i][0]) + ",'" + services_status[i][2] + "','" + time.strftime('%Y-%m-%d %H:%M:%S') + "'),"

        updates_query = "INSERT INTO TBL_Services_Updates (service_id,status,last_update) VALUES " +\
                        status_part[:-1] + ";"

        update_status(updates_query)

        time.sleep(time_to_wait)
