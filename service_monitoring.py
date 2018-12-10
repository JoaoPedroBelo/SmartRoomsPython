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

    # Get existing services from database
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
        status = os.system('systemctl status ' + "api.service" + ' > /dev/null')


        for p in all_process_ids:
            p_aux = psutil.Process(p)
            print(p_aux.status())
            for value in p_aux.cmdline():
                for i in range(len(services_status)):
                    if value == services_status[i][0]:
                        services_status[i][1] = p_aux.status()

        print(services_status)

        # QUERY
        # UPDATE TBL_Services
        #    SET status = CASE id
        #                       WHEN 1 THEN 12
        #                       WHEN 2 THEN 22
        #                       WHEN 3 THEN 33
        #                       ELSE status
        #                       END
        #  WHERE id IN(1, 2, 3);

        time.sleep(time_to_wait)
