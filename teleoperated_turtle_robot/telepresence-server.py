#!/usr/bin/env python3

import socket
from gpiozero import Motor, OutputDevice
from time import sleep
from time import time
import sys

# Define and setup GPIO pins
# Rigth foot
motor1 = Motor(24, 27)
motor1_enable = OutputDevice(5, initial_value=1)
# Left foot
motor2 = Motor(6, 22)
motor2_enable = OutputDevice(17, initial_value=1)
# Right tentacle
motor3 = Motor(23, 16)
motor3_enable = OutputDevice(12, initial_value=1)
# Left tentacle
motor4 = Motor(13, 18)
motor4_enable = OutputDevice(25, initial_value=1) 

# HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65443  # Port to listen on (non-privileged ports are > 1023)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

time_old = time()
flag_wings = True


def pos_to_command(x, y):
    """
    Translates position of hand detected to command sent to robot
    """
    # Cap max and min x values 
    if x < 0.0:
        x = 0

    if x > 1.0:
        x = 1   

    # Map position to command      
    if x < 0.4:        # Turn left
        out = 'left'
         
    elif x > 0.6:        # Turn right 
        out = 'right'
        
    else:                # Go forwards
        out = 'forward'


    return out



while(1):

    # # Switch wing direction every 3s
    # time_new = time()
    # if time_new-time_old >= 3:
    #     time_old = time_new
    #     print('switched wing direction')

    # # Switch wings on/off
    # if flag_wings:
    #     print('wings up')
    #     motor3.forward()
    #     motor4.forward()
    # else:
    #     print('wings down')
    #     motor3.stop()
    #     motor4.stop()

    # print('looper')



    conn, addr = server_socket.accept()
    with conn:
        print(f"Connected by {addr}")



        while True:

            # time_new = time()
            # if time_new-time_old >= 2:
            #     flag_wings = not flag_wings
            #     time_old = time_new
                        #     #sleep(2)

            # # # Switch wings on/off
            #     if flag_wings:
            #         print('wings up')
            #         motor3.forward()
            #         motor4.forward()
            #     else:
            #         print('wings down')
            #         motor3.stop()
            #         motor4.stop()




            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode()
            print(msg)


            # if msg != 'no command' and msg != 'stop':
            if msg not in ['no command', 'stop', 'forward', 'backward', 'right', 'left']:

                coordinates = msg.split(',')

                # Convert string to floating point data 
                coordinates = [float(i) for i in coordinates]

                # Grouped coordinates as nested list of x,y pairs for each hand detected
                hands = [coordinates[i:i+2] for i in range(0, len(coordinates), 2)]

                # print(coordinates)

                # If 2 hands detected:
                if len(hands) > 1:

                    # If x coordinate of both hands are on the same side of the screen, ignore one hand
                    print("2 hands detected. Change n_hands to '1' in client code...")
                    print("Exiting program...")
                    sys.exit(1)


                # For each hand 
                for i in hands:

                    x_position = i[0]
                    y_position = i[1]
                    print(x_position) 

                    msg = pos_to_command(x_position, y_position)
                    print('msg', msg)


            if msg == 'stop':
                motor1.stop() 
                motor2.stop()
                motor3.stop() 
                motor4.stop()

            elif msg == 'left':
                motor1.stop()
                motor2.forward()

            elif msg == 'right':
                motor1.forward()
                motor2.stop()
                
            elif msg == 'forward':
                motor1.forward()
                motor2.forward()
                
            #conn.sendall(data)
    
    # except:
    #     print('no comms')


# except KeyboardInterrupt:
#         pass

