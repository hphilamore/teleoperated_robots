#!/usr/bin/env python3

import socket
from gpiozero import Motor, OutputDevice
from time import sleep
from time import time
import sys

# HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65443  # Port to listen on (non-privileged ports are > 1023)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

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

# Variables to make the robot lift and lower wings every N seconds 
time_old = time()
flag_wings = True
wing_period = 2


# def pos_to_command(x, y):
#     """
#     Translates position of hand detected to command sent to robot
#     """
#     # Cap max and min x values 
#     if x < 0.0:
#         x = 0

#     if x > 1.0:
#         x = 1   

#     # Map position to command      
#     if x < 0.4:        # Turn left
#         out = 'left'
         
#     elif x > 0.6:        # Turn right 
#         out = 'right'
        
#     else:                # Go forwards
#         out = 'forward'


#     return out

def pose_to_command(msg):
    """
    Translates pose detected to command sent to robot
    """
    try:
        # Get coordinates of each node sent
        nose = msg["NOSE"]
        hip_l = msg["LEFT_HIP"]
        hip_r = msg["RIGHT_HIP"]
        hand_l = msg["LEFT_WRIST"]
        hand_r = msg["RIGHT_WRIST"]

        print('left_hand', hand_l)
        print('right_hand', hand_r)
        print('left_hip', hip_l)
        print('right_hip', hip_r)
        print('nose', nose)

        # If hands above head, go forwards
        if hand_l[y] <= nose[y] and hand_r[y] <= nose[y]:
            command = 'forward'

        # If hands below hips, go backwards 
        elif hand_l[y] >= hip_l[y] and hand_r[y] >= hip_r[y]:
            command = 'backward'

        # If both hands left of left hip, turn left 
        elif hand_l[x] < hip_l[x] and hand_r[x] < hip_l[x]:
            command = 'left'
            # command = 'right' # video sphere as mirror world

        # If both hands right of right hip, turn right 
        elif hand_l[x] > hip_r[x] and hand_r[x] > hip_r[x]:
            command = 'right'
            # command = 'left' # video sphere as mirror world 

        # If hands either side of body and vertical position is between nose and hips 
        elif hand_l[x] < nose[x] and hand_r[x] > nose[x]:
            command = 'stop'

        # If none of these poses are detected, no change 
        else:
            command = 'no command'

    except:
        print("Warning: Nodes required for pose detection not in data sent to robot!")
        command = 'no command'

    print(command)
    return command


def Stopmotors():
    motor1.stop() 
    motor2.stop()
    motor3.stop() 
    motor4.stop()

def Spin_Left():
    motor1.stop()
    motor2.forward()

def Spin_Right(): 
    motor1.forward()
    motor2.stop()

def Forwards(): 
    motor1.forward()
    motor2.forward()
        

if __name__ == "__main__":

    while True:

        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")

            while True:

                # Switch wing direction every N seconds 
                # time_new = time()
                # if time_new-time_old >= wing_period:
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

                # Break out of loop if no data received
                if not data:
                    break

                msg = data.decode()
                print(msg)


                # If message recieved is not already in form of a command
                if msg not in ['no command', 'stop', 'forward', 'backward', 'right', 'left']:

                    # convert string-dictionary of node coordinates to dictionary
                    msg = json.loads(msg)

                    print('msg2', type(msg), msg)

                    # Convert pose to robot command
                    command = pose_to_command(msg)

                else:
                    command = msg

                if command == 'stop':
                    Stopmotors()

                elif command == 'left':
                    Spin_Left()

                elif command == 'right':
                    Spin_Right()

                elif command == 'forward':
                    Forwards()

                elif command == 'backward':
                    Stopmotors()



                    # coordinates = msg.split(',')

                    # # Convert string to floating point data 
                    # coordinates = [float(i) for i in coordinates]

                    # # Grouped coordintes 2D (x,y) or 3D (x,y,z) for each hand detected
                    # n_dimensions = 2 # x,y,z coordinates recieved 
                    # hands = [coordinates[i:i+n_dimensions] for i in range(0, len(coordinates), n_dimensions)]


                    # # print(coordinates)

                    # # If 2 hands detected:
                    # if len(hands) > 1:

                    #     # If x coordinate of both hands are on the same side of the screen, ignore one hand
                    #     print("2 hands detected. Change n_hands to '1' in client code...")
                    #     print("Exiting program...")
                    #     sys.exit(1)


                    # # For each hand 
                    # for i in hands:

                    #     x_position = i[0]
                    #     y_position = i[1]
                    #     print(x_position) 

                    #     msg = pos_to_command(x_position, y_position)
                    #     print('msg', msg)



                    
                #conn.sendall(data)

        # except:
        #     print('no comms')


        # except KeyboardInterrupt:
        #         pass

