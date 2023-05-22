#!/usr/bin/env python3

import socket
# from gpiozero import Motor, OutputDevice
from time import sleep
from time import time
import RPi.GPIO as GPIO

# # Define and setup GPIO pins
# # Rigth foot
# motor1 = Motor(24, 27)
# motor1_enable = OutputDevice(5, initial_value=1)
# # Left foot
# motor2 = Motor(6, 22)
# motor2_enable = OutputDevice(17, initial_value=1)
# # Right tentacle
# motor3 = Motor(23, 16)
# motor3_enable = OutputDevice(12, initial_value=1)
# # Left tentacle
# motor4 = Motor(13, 18)
# motor4_enable = OutputDevice(25, initial_value=1) 


# Setup-server socket
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65442  # Port to listen on (non-privileged ports are > 1023)
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


def pos_to_command(x, y):
    """
    Translates position of hand detected to command sent to robot
    """
    if 0.0 < x < 1.0:        # Check hand detected in frame        

        if x < 0.4:        # Turn left
            out = 'left'
             
        elif x > 0.6:        # Turn right 
            out = 'right'
            
        else:                # Go forwards
            if y >= 0.5:
                out = 'backward'
            else:
                out = 'forward'

    else:
        out = 'none'

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
            print(msg)

            # if msg != 'no hand' and msg != 'stop':
            if msg not in ['no hand', 'stop', 'forward', 'backward', 'right', 'left']

                coordinates = msg.split(',')

                coordinates = [float(i) for i in coordinates]

                # Grouped coordintes
                coordinates = [coordinates[i:i+2] for i in range(0, len(coordinates), 2)]

                print(coordinates)

                msg = pos_to_command(coordinates[0], coordinates[1])


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


            #conn.sendall(data)
    
    # except:
    #     print('no comms')


# except KeyboardInterrupt:
#         pass

