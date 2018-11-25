from datetime import datetime
from random import randint
import time
import socket
import keyboard


server_address = ('localhost', 6789)
max_size = 4096

print('Starting the client at', datetime.now())
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:  # making a loop
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed
            print('Q key pressed.')
            print('Stopping server.')
            client.sendto(b'stop', server_address)
            break  # finishing the loop
        else:
            pass
    except:
        break  # if user pressed a key other than the given key the loop will break

    DELAY = randint(60, 120)  # !DELAY! (supostamente é 1segundo +-)

    time.sleep(DELAY)
    fail = 4
    chance = 50  # chance de entrar ou sair um grupo de pessoas
    chanceSensorActivate = 1  # chance de uma pessoa passar no sensor
    Bsize = 5  # tamanho maximo do grupo
    behavior = randint(0, chanceSensorActivate)  # 1 entrada 2 é saida

    if behavior == 1:  # Uma pessoa no sensor
        SensorActivate = randint(0, 1)
        if SensorActivate == 0:  # Entrada
            rooms = randint(0, fail)
            Sensor_Out = 1
            print()
            print("Sensor fora activado")
            time.sleep(0.2)
            Sensor_Out = 0

            Sensor_In = 1
            print("Sensor dentro activado")
            print()

            if rooms < 4:
                sensordata = (str(SensorActivate) + ',' + str(rooms))
                print(sensordata)
                print()
                client.sendto(sensordata.encode(), server_address)
                data, server = client.recvfrom(max_size)
                print('SERVER RESPONSE: ', data.decode('UTF-8'), '  at  ', datetime.now())

                group = randint(1, chance)

                if group == 1:
                    size = randint(1, Bsize)
                    for x in range(0, size):
                        sensordata = (str(SensorActivate) + ',' + str(rooms))
                        print(sensordata)
                        print()
                        client.sendto(sensordata.encode(), server_address)
                        data, server = client.recvfrom(max_size)
                        print('SERVER RESPONSE: ', data.decode('UTF-8'), '  at  ', datetime.now())

            Sensor_In = 0

        elif SensorActivate == 1:  # Saida
            rooms = randint(1, fail)
            print()
            print("Sensor dentro activado")
            Sensor_In = 1
            time.sleep(0.2)
            print("Sensor fora activado")
            print()
            Sensor_In = 0
            Sensor_Out = 1
            if rooms < 4:

                sensordata = (str(SensorActivate) + ',' + str(rooms))
                print(sensordata)
                print()
                client.sendto(sensordata.encode(), server_address)
                data, server = client.recvfrom(max_size)
                print('SERVER RESPONSE: ', data.decode('UTF-8'), '  at  ', datetime.now())

                group = randint(1, chance)

                if group == 1:
                    size = randint(1, Bsize)
                    for x in range(0, size):

                        sensordata = (str(SensorActivate) + ',' + str(rooms))
                        print(sensordata)
                        print()
                        client.sendto(sensordata.encode(), server_address)
                        data, server = client.recvfrom(max_size)
                        print('SERVER RESPONSE: ', data.decode('UTF-8'), '  at  ', datetime.now())

            Sensor_Out = 0

print("Stopping client.")
client.close()
