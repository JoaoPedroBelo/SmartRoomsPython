from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import pyodbc
from datetime import datetime
from constants import values, functions

functions.start_logging("/home/pi/projeto/notification.log")


def connect_database():
    try:
        cnxn = pyodbc.connect(values.connection_string)
        functions.message(str(datetime.now()) + ': ' + "Database Connection Successfull")
        return cnxn
    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        functions.message(str(datetime.now()) + ': ' + "ERROR_DATABASE_CONNECTION: " + sqlstate)
        return False


def send_email(par_email, par_message):
    # create message object instance
    msg = MIMEMultipart()

    # setup the parameters of the message
    password = "SDgrupo3_projecto"
    msg['From'] = "smartstudyrooms@gmail.com"
    msg['To'] = par_email
    msg['Subject'] = "Notification Rooms"

    # add in the message body
    msg.attach(MIMEText(par_message, 'plain'))

    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()

    # Login Credentials for sending the mail
    server.login(msg['From'], password)

    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    server.quit()

    functions.message("successfully sent email to %s:" % (msg['To']))


def get_users_subscrive(par_cursor):
    users_data = []
    try:
        par_cursor.execute("select TBL_Account.id from TBL_Account, TBL_Account_has_TBL_Salas "
                           "where TBL_Account.id= TBL_Account_has_TBL_Salas.TBL_Account_id group by TBL_Account.id")
        data = par_cursor.fetchall()
        for row in data:
            users_data.append(list(row))
    except pyodbc.Error as e:
        functions.message(str(datetime.now()) + ': ' + "ERROR getting room capacity from DB: " + str(e))
        return False
    return users_data


def get_user_rooms_data(par_cursor, par_user_id):
    rooms_data = []
    try:
        par_cursor.execute("select email, tbl_salas.nome_sala, occupied_seats, empty_seats, TBL_Eventos.time "
                           "from TBL_Eventos,TBL_Salas, TBL_Account, TBL_Account_has_TBL_Salas "
                           "where TBL_Eventos.time =( select max(TBL_Eventos.time) "
                           "from TBL_Eventos "
                           "where TBL_Eventos.TBL_Salas_id=TBL_Salas.id "
                           "and TBL_Account.id=TBL_Account_has_TBL_Salas.TBL_Account_id "
                           "and TBL_Account_has_TBL_Salas.TBL_Salas_id = TBL_Salas.id "
                           "and TBL_Account.id="+str(par_user_id)+")")
        data = par_cursor.fetchall()
        for row in data:
            rooms_data.append(list(row))
    except pyodbc.Error as e:
        functions.message(str(datetime.now()) + ': ' + "ERROR getting room capacity from DB: " + str(e))
        return False
    return rooms_data


if __name__ == "__main__":
    connection = connect_database()
    cursor = connection.cursor()
    message = "the information about the room you have chosen: " + '\n'
    email = ""
    for user in get_users_subscrive(cursor):
        for rooms in get_user_rooms_data(cursor, user[0]):
            email = rooms[0]
            message += str(rooms[2]) + " empty seats in " + rooms[1] + '\n' + str(rooms[3])\
                       + " ocupied seats in " + rooms[1] + '\n'
        message += '\n'+"To unsubscribe visite the website insert your email and uncheck all the boxes."
        send_email(email, message)
        message = "the information of the room you have chosen: " + '\n'  # limpa mensagem depois do ciclo

