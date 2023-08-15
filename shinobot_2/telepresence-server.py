#!/usr/bin/env python3

import socket
# from gpiozero import Motor, OutputDevice
from time import sleep
from time import time
import RPi.GPIO as GPIO
import json


# Setup-server socket
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65447  # Port to listen on (non-privileged ports are > 1023)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()


time_old = time()
flag_wings = True

# Set the GPIO mode (pin numbers)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set variables for the GPIO motor pins
Motor1A = 6
Motor1B = 13
Motor2A = 20
Motor2B = 21
EnableA = 12
EnableB = 26
#pinTrigger = 17
#pinEcho = 18

# How many times to turn the pin on and off each second
Frequency = 20

# How long the pin stays on each cycle, as a percent 
DutyCycle = 20

# Setting the duty cycle to 0 means the motors will not turn
Stop = 0

# Number of dimensions of recieved coordinates e.g. 3 = x,y,z coordinates recieved 
n_dimensions = 3

# Set the GPIO Pin mode to be Output
GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(EnableA, GPIO.OUT)
GPIO.setup(EnableB, GPIO.OUT)

# Set the GPIO to software PWM at 'Frequency' Hertz
PWM_Motor1A = GPIO.PWM(Motor1A, Frequency)
PWM_Motor1B = GPIO.PWM(Motor1B, Frequency)
PWM_Motor2A = GPIO.PWM(Motor2A, Frequency)
PWM_Motor2B = GPIO.PWM(Motor2B, Frequency)

# Start the software PWM with a duty cycle of 0 (i.e. not moving)
PWM_Motor1A.start(Stop)
PWM_Motor1B.start(Stop)
PWM_Motor2A.start(Stop)
PWM_Motor2B.start(Stop)

def Enable(state):
    """ 
    When state is 0, enable pin is driven high, PWM output
    """
    GPIO.output(EnableA, state)
    GPIO.output(EnableB, state)

def StopMotors():
    """
    Turn all motors off
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(Stop)
    PWM_Motor2A.ChangeDutyCycle(Stop)
    PWM_Motor2B.ChangeDutyCycle(Stop)

def Forwards():
    """
    Turn both motors forwards
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(DutyCycle)
    PWM_Motor2A.ChangeDutyCycle(DutyCycle)
    PWM_Motor2B.ChangeDutyCycle(Stop)

def Backwards():
    """
    Turn both motors backwards
    """
    PWM_Motor1A.ChangeDutyCycle(DutyCycle)
    PWM_Motor1B.ChangeDutyCycle(Stop)
    PWM_Motor2A.ChangeDutyCycle(Stop)
    PWM_Motor2B.ChangeDutyCycle(DutyCycle)

def Spin_Right():
    """
    Turn left
    """
    PWM_Motor1A.ChangeDutyCycle(DutyCycle)
    PWM_Motor1B.ChangeDutyCycle(Stop)
    PWM_Motor2A.ChangeDutyCycle(DutyCycle)
    PWM_Motor2B.ChangeDutyCycle(Stop)

def Spin_Left():
    """
    Turn Right
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(DutyCycle)
    PWM_Motor2A.ChangeDutyCycle(Stop)
    PWM_Motor2B.ChangeDutyCycle(DutyCycle)

def Turn_Right():
    """
    Turn left
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(DutyCycle/3)
    PWM_Motor2A.ChangeDutyCycle(DutyCycle)
    PWM_Motor2B.ChangeDutyCycle(Stop)

def Turn_Left():
    """
    Turn Right
    """
    PWM_Motor1A.ChangeDutyCycle(Stop)
    PWM_Motor1B.ChangeDutyCycle(DutyCycle)
    PWM_Motor2A.ChangeDutyCycle(DutyCycle/3)
    PWM_Motor2B.ChangeDutyCycle(Stop)


def pos_to_command(hands):
    """
    Translates position of hand detected to command sent to robot
    """
    print('left', hands[0])
    print('right', hands[1])

    # if both hands on left, turn left
    if hands[0][0] < 0.3 and hands[1][0] < 0.3:
        out = 'left'

    # if both hands on right, turn right
    elif hands[0][0] > 0.7 and hands[1][0] > 0.7:
        out = 'right'

    # if one hand on left and one hand on right, stop
    elif (hands[0][0] > 0.7 and hands[1][0] < 0.3 or
          hands[0][0] < 0.3 and hands[1][0] > 0.7):
        out = 'stop'

    # if both hands in centre... 
    else:                
        # ...and high, go forward
        if hands[0][1] < 0.5 and hands[1][1] < 0.5:
            out = 'forward'
        # ...and low, go backwards
        else:
            out = 'backward'
            

    return out


while(1):

    Enable(1)

    conn, addr = server_socket.accept()
    with conn:
        print(f"Connected by {addr}")

        while True:

            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode()
            # print(msg)

            # if msg != 'no command' and msg != 'stop':
            if msg not in ['no command', 'stop', 'forward', 'backward', 'right', 'left']:

                # coordinates = msg.split(',')

                # # Convert string to floating point data 
                # coordinates = [float(i) for i in coordinates]

                # # Nest coordintes 2D (x,y) or 3D (x,y,z) for each hand detected
                # hands = [coordinates[i:i+n_dimensions] for i in range(0, len(coordinates), n_dimensions)]


                # msg = pos_to_command(hands)
                print('msg1', type(msg), msg)

                # convert dictionary string to dictionary
                msg = json.loads(msg)

                print('msg2', type(msg), msg)


            if msg == 'stop':
                StopMotors()


            elif msg == 'left':
                Spin_Left()


            elif msg == 'right':
                Spin_Right()

                

            elif msg == 'forward':
                Forwards()


            elif msg == 'backward':
                Backwards()

