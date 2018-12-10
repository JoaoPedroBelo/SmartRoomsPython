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

        cursor.execute(query)  # Insert new event if room isnt empty

        all_services = cursor.execute(query).fetchall()

        services_status = []
        for row in all_services:
            services_status.append([row[2],'stopped'])

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
            status = os.system('systemctl status ' + services_status[i][0] + ' > /dev/null')
            if status == 0:
                services_status[i][1] = 'Ok'
            else:
                services_status[i][1] = 'Dead'

            status_part += " WHEN '" + services_status[i][0] + "' THEN '" + services_status[i][1] + "'"

        update_query = "UPDATE TBL_Services " \
                       "SET status = CASE service_name " + status_part + \
                       " ELSE status" \
                       " END, last_update = '" + time.strftime('%Y-%m-%d %H:%M:%S') + "'" + \
                       " WHERE service_name IN('sensors.service','server.service','api.service')"

        update_status(update_query)

        time.sleep(time_to_wait)
