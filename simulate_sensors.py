from datetime import datetime
from random import randint
import time
import socket
# para o raspberry
# import logging
# alterar todos os prints para logging.info
# adicionar no inicio logging.basicConfig(filename='write_data_script.log',level=logging.DEBUG)


def send_data(par_sensoractivate, par_rooms):
    sensordata = (str(par_sensoractivate) + ',' + str(par_rooms))
    print(sensordata+'\n')
    client.sendto(sensordata.encode(), server_address)
    data, server = client.recvfrom(max_size)
    print('SERVER RESPONSE: ', data.decode('UTF-8'), '  at  ', datetime.now())


def generate_persons(par_night, par_day):
    now = datetime.now()
    if not verify_weekend():
        if par_day <= now.hour <= par_night:
            return 2   # chance de uma pessoa passar no sensor 50%
        else:
            return 10  # chance de uma pessoa passar no sensor 10%
    else:
        return 10  # chance de uma pessoa passar no sensor 10%


def verify_weekend():

    if datetime.today().weekday() == 5 or datetime.today().weekday() == 6:
        return True
    else:
        return False


def generate_in_out():
    now = datetime.now()
    if 8 <= now.hour <= 10:
        in_out = randint(1, 5)
        if in_out != 1:
            return 0  # Entrada
        else:
            return 1  # Saida
    elif 18 <= now.hour <= 19:
        in_out = randint(1, 5)
        if in_out != 1:
            return 1  # Saida
        else:
            return 0   # Entrada
    else:
        in_out = randint(0, 1)
        return in_out


server_address = ('localhost', 6789)
max_size = 4096

print('Starting the client at', datetime.now())
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:  # making a loop
    fail = 5     # probablidade de falhar
    chance = 50  # chance de entrar ou sair um grupo de pessoas
    Bsize = 5  # tamanho maximo do grupo
    night = 21   # hora que começa a noite
    day = 8      # hora que começa o dia
    behavior = randint(1, generate_persons(night, day))  # 1 significa sensor ativado

    if behavior == 1:  # Uma pessoa no sensor
        SensorActivate = generate_in_out()
        if SensorActivate == 0:  # !! Entrada
            rooms = randint(0, fail)
            if rooms < 4:
                # Sensor_Out = 1 # Sensor de fora activa

                print('\n'+"Sensor fora ativado")
                time.sleep(0.2)
                # Sensor_Out = 0 # Sensor de fora desativa
                # Sensor_In = 1 # Sensor de dentro activa
                print("Sensor dentro activado"+'\n')
                send_data(1, rooms)
                group = randint(1, chance)
                if group == 1:
                    size = randint(1, Bsize)
                    for x in range(0, size):
                        send_data(1, rooms)
            # Sensor_In = 0 # Sensor de dentro desativa

        elif SensorActivate == 1:  # !! Saida
            rooms = randint(0, fail)
            if rooms < 4:
                print('\n'+"Sensor dentro ativado")
                # Sensor_In = 1 # Sensor de dentro ativa
                time.sleep(0.2)
                print("Sensor fora ativado"+'\n')
                # Sensor_In = 0 # Sensor de dentro desativa
                # Sensor_Out = 1 # Sensor de fora ativa
                send_data(-1, rooms)
                group = randint(1, chance)
                if group == 1:
                    size = randint(1, Bsize)
                    for x in range(0, size):
                        send_data(-1, rooms)
            # Sensor_Out = 0 # Sensor de fora ativa

    DELAY = randint(60, 120)  # !DELAY! (supostamente é 1segundo +-)
    verify_weekend()
    print("delay: ")
    print(DELAY)
    time.sleep(DELAY)

print("Stopping client.")
client.close()


