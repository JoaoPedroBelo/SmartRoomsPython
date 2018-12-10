from datetime import datetime
from random import randint
import time
import socket
from constants import functions


def send_data(par_sensoractivate, par_rooms):
    sensordata = (str(par_sensoractivate) + ',' + str(par_rooms))
    functions.message(str(datetime.now()) + ': ' + sensordata+'\n')
    client.sendto(sensordata.encode(), server_address)
    data, server = client.recvfrom(max_size)
    functions.message(str(datetime.now()) + ': ' + 'SERVER RESPONSE: '+ str(data.decode('UTF-8'))+ '  at  '
                      + str(datetime.now()))


def generate_persons(par_night, par_day):
    now = datetime.now()
    if not verify_weekend():
        if par_day <= now.hour <= par_night:
            if 8 <= now.hour <= 11 or 17 <= now.hour <= 21:
                return 1   # chance de uma pessoa passar no sensor em hora de entrada ou saida
            else:
                return 2    # em horas normais
        else:
            return 50  # chance de uma pessoa passar a noite
    else:
        return 50  # chance de uma pessoa passar ao fim de semana


def verify_weekend():

    if datetime.today().weekday() == 5 or datetime.today().weekday() == 6:
        return True
    else:
        return False


def generate_in_out():
    now = datetime.now()

    if 8 <= now.hour <= 11:
        in_out = randint(1, 20)
        if in_out != 1:
            return 0  # Entrada
        else:
            return 1  # Saida
    elif 17 <= now.hour <= 20:
        in_out = randint(1, 20)
        if in_out != 1:
            return 1  # Saida
        else:
            return 0   # Entrada
    else:
        in_out = randint(0, 1)
        return in_out


functions.start_logging('/home/pi/projeto/simulate_sensors.log')
server_address = ('localhost', 6789)
max_size = 4096

functions.message(str(datetime.now()) + ': ' + 'Starting the client.')
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
first_time_run = 0  # Primeira vez que o programa é executado
while True:  # making a loop
    fail = 3     # probablidade de falhar
    chance = 50  # chance de entrar ou sair um grupo de pessoas
    Bsize = 5  # tamanho maximo do grupo
    night = 21   # hora que começa a noite
    day = 8      # hora que começa o dia

    if first_time_run != 0:
        behavior = randint(1, generate_persons(night, day))  # 1 significa sensor ativado
    else:
        behavior = 1
        first_time_run = 1

    if behavior == 1:  # Uma pessoa no sensor
        SensorActivate = generate_in_out()
        if SensorActivate == 0:  # !! Entrada
            rooms = randint(0, fail)
            if rooms < 4:
                # Sensor_Out = 1 # Sensor de fora activa

                functions.message(str(datetime.now()) + ': ' + "Sensor fora ativado"+'\n')
                time.sleep(0.2)
                # Sensor_Out = 0 # Sensor de fora desativa
                # Sensor_In = 1 # Sensor de dentro activa
                functions.message(str(datetime.now()) + ': ' + "Sensor dentro activado"+'\n')
                send_data(1, rooms)
                group = randint(1, chance)
                if group == 1:
                    size = randint(1, Bsize)
                    for x in range(0, size):
                        print('\n' + "Sensor fora ativado")
                        time.sleep(0.2)
                        print("Sensor dentro activado" + '\n')
                        send_data(1, rooms)
            # Sensor_In = 0 # Sensor de dentro desativa
        elif SensorActivate == 1:  # !! Saida
            rooms = randint(0, fail)
            if rooms < 4:
                functions.message(str(datetime.now()) + ': ' + "Sensor dentro ativado"+'\n')
                # Sensor_In = 1 # Sensor de dentro ativa
                time.sleep(0.2)
                functions.message(str(datetime.now()) + ': ' + "Sensor fora ativado"+'\n')
                # Sensor_In = 0 # Sensor de dentro desativa
                # Sensor_Out = 1 # Sensor de fora ativa
                send_data(-1, rooms)
                group = randint(1, chance)
                if group == 1:
                    size = randint(1, Bsize)
                    for x in range(0, size):
                        print('\n' + "Sensor dentro ativado") #
                        time.sleep(0.2)
                        print("Sensor fora ativado" + '\n')
                        send_data(-1, rooms)
            # Sensor_Out = 0 # Sensor de fora ativa

    DELAY = randint(60, 120)  # !DELAY! (supostamente é 1segundo +-)
    functions.message(str(datetime.now()) + ': ' + "delay: ")
    functions.message(str(datetime.now()) + ': ' + str(DELAY))
    time.sleep(DELAY)

functions.message(str(datetime.now()) + ': ' + "Stopping client.")
client.close()
