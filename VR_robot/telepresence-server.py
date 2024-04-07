#!/usr/bin/env python3

import socket
# from gpiozero import motor, OutputDevice
from time import sleep
from time import time
import RPi.GPIO as GPIO
import json

# Setup-server socket
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65448  # Port to listen on (non-privileged ports are > 1023)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# Set the GPIO mode (pin numbering system)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup GPIO motor pins
motor1A = 6
motor1B = 13
motor2A = 20
motor2B = 21
enableA = 12
enableB = 26
#pinTrigger = 17
#pinEcho = 18

# How many times to turn the pin on and off each second
frequency = 20

# How long the pin stays on each cycle, as a percent 
DutyCycle = 100

# Setting the duty cycle to 0 means the motors will not turn
Stop = 0

# # Number of dimensions of recieved coordinates e.g. 3 = x,y,z coordinates recieved 
# n_dimensions = 3

# Indexing of xyz coordinates
x = 0
y = 1
z = 2

# Set the GPIO Pin mode to be Output
GPIO.setup(motor1A, GPIO.OUT)
GPIO.setup(motor1B, GPIO.OUT)
GPIO.setup(motor2A, GPIO.OUT)
GPIO.setup(motor2B, GPIO.OUT)
GPIO.setup(enableA, GPIO.OUT)
GPIO.setup(enableB, GPIO.OUT)

# Set the GPIO to software PWM at 'frequency' Hertz
PWM_motor1A = GPIO.PWM(motor1A, frequency)
PWM_motor1B = GPIO.PWM(motor1B, frequency)
PWM_motor2A = GPIO.PWM(motor2A, frequency)
PWM_motor2B = GPIO.PWM(motor2B, frequency)

# Start the software PWM with a duty cycle of 0 (i.e. not moving)
PWM_motor1A.start(Stop)
PWM_motor1B.start(Stop)
PWM_motor2A.start(Stop)
PWM_motor2B.start(Stop)


def enable(state):
    """ 
    When state is 0, enable pin is driven high, PWM output
    """
    GPIO.output(enableA, state)
    GPIO.output(enableB, state)

def Stopmotors():
    """
    Turn all motors off
    """
    PWM_motor1A.ChangeDutyCycle(Stop)
    PWM_motor1B.ChangeDutyCycle(Stop)
    PWM_motor2A.ChangeDutyCycle(Stop)
    PWM_motor2B.ChangeDutyCycle(Stop)

def Forwards():
    """
    Turn both motors forwards
    """
    PWM_motor1A.ChangeDutyCycle(Stop)
    PWM_motor1B.ChangeDutyCycle(DutyCycle)
    PWM_motor2A.ChangeDutyCycle(DutyCycle)
    PWM_motor2B.ChangeDutyCycle(Stop)

def Backwards():
    """
    Turn both motors backwards
    """
    PWM_motor1A.ChangeDutyCycle(DutyCycle)
    PWM_motor1B.ChangeDutyCycle(Stop)
    PWM_motor2A.ChangeDutyCycle(Stop)
    PWM_motor2B.ChangeDutyCycle(DutyCycle)

def Spin_Right():
    """
    Turn left
    """
    PWM_motor1A.ChangeDutyCycle(DutyCycle)
    PWM_motor1B.ChangeDutyCycle(Stop)
    PWM_motor2A.ChangeDutyCycle(DutyCycle)
    PWM_motor2B.ChangeDutyCycle(Stop)

def Spin_Left():
    """
    Turn Right
    """
    PWM_motor1A.ChangeDutyCycle(Stop)
    PWM_motor1B.ChangeDutyCycle(DutyCycle)
    PWM_motor2A.ChangeDutyCycle(Stop)
    PWM_motor2B.ChangeDutyCycle(DutyCycle)

def Turn_Right():
    """
    Turn left
    """
    PWM_motor1A.ChangeDutyCycle(Stop)
    PWM_motor1B.ChangeDutyCycle(DutyCycle/3)
    PWM_motor2A.ChangeDutyCycle(DutyCycle)
    PWM_motor2B.ChangeDutyCycle(Stop)

def Turn_Left():
    """
    Turn Right
    """
    PWM_motor1A.ChangeDutyCycle(Stop)
    PWM_motor1B.ChangeDutyCycle(DutyCycle)
    PWM_motor2A.ChangeDutyCycle(DutyCycle/3)
    PWM_motor2B.ChangeDutyCycle(Stop)


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

        print('left_hand \t', hand_l)
        print('right_hand \t', hand_r)
        print('left_hip \t', hip_l)
        print('right_hip \t', hip_r)
        print('nose \t', nose)

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
    

if __name__ == "__main__":


    while True:

        enable(1)

        conn, addr = server_socket.accept()
        with conn:
            # print(f"Connected by {addr}")

            while True:

                data = conn.recv(1024)

                # Break out of loop if no data received
                if not data:
                    break

                msg = data.decode()

                # If message recieved is not already in form of a command
                if msg not in ['no command', 'stop', 'forward', 'backward', 'right', 'left']:

                    # convert string-dictionary of node coordinates to dictionary
                    msg = json.loads(msg)

                    # print('msg2', type(msg), msg)

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
                    Backwards()
