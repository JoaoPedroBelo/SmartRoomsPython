from datetime import datetime
from random import randint
import time
import socket


def send_Data(SensorActivate, rooms):
    sensordata = (str(SensorActivate) + ',' + str(rooms))
    print(sensordata)
    print()
    client.sendto(sensordata.encode(), server_address)
    data, server = client.recvfrom(max_size)
    print('SERVER RESPONSE: ', data.decode('UTF-8'), '  at  ', datetime.now())


server_address = ('localhost', 6789)
max_size = 4096

print('Starting the client at', datetime.now())
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:  # making a loop
    fail = 5     #probablidade de falhar
    chance = 50  # chance de entrar ou sair um grupo de pessoas
    chanceSensorActivate = 1  # chance de uma pessoa passar no sensor
    Bsize = 5  # tamanho maximo do grupo
    behavior = randint(0, chanceSensorActivate)  # 1 entrada 2 é saida

    if behavior == 1:  # Uma pessoa no sensor
        SensorActivate = randint(0, 1)
        if SensorActivate == 0:  #!! Entrada
            rooms = randint(0, fail)
            if rooms < 4:
                #Sensor_Out = 1 #Sensor de fora activa
                print()
                print("Sensor fora ativado")
                time.sleep(0.2)
                #Sensor_Out = 0 #Sensor de fora desativa
                #Sensor_In = 1 #Sensor de dentro activa
                print("Sensor dentro activado")
                print()
                send_Data(SensorActivate, rooms)
                group = randint(1, chance)
                if group == 1:
                    size = randint(1, Bsize)
                    for x in range(0, size):
                        send_Data(SensorActivate, rooms)
            #Sensor_In = 0 #Sensor de dentro desativa

        elif SensorActivate == 1:  #!! Saida
            rooms = randint(0, fail)
            if rooms < 4:
                print()
                print("Sensor dentro ativado")
                #Sensor_In = 1 #Sensor de dentro ativa
                time.sleep(0.2)
                print("Sensor fora ativado")
                print()
                #Sensor_In = 0 #Sensor de dentro desativa
                #Sensor_Out = 1 #Sensor de fora ativa
                send_Data(SensorActivate, rooms)
                group = randint(1, chance)
                if group == 1:
                    size = randint(1, Bsize)
                    for x in range(0, size):
                        send_Data(SensorActivate, rooms)
            #Sensor_Out = 0 #Sensor de fora ativa

    DELAY = randint(60, 120)  # !DELAY! (supostamente é 1segundo +-)
    print("delay: ")
    print(DELAY)
    time.sleep(DELAY)

print("Stopping client.")
client.close()


