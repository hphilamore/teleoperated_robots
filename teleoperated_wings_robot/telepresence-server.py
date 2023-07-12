#!/usr/bin/env python3

"""

TODO:
- servo should read current positions and not do a full rotation when returning to start position
- Close port if program crashes so that new number doesn’t have to be used 
- GPIO all pins to zero when program killed (e.g. no motors left spinning)
    - https://raspi.tv/2013/rpi-gpio-basics-3-how-to-exit-gpio-programs-cleanly-avoid-warnings-and-protect-your-pi
    - https://gpiozero.readthedocs.io/en/stable/migrating_from_rpigpio.html

"""

import socket
# from gpiozero import Motor, OutputDevice
from time import sleep
from time import time
import numpy as np
import RPi.GPIO as GPIO
import serial
import os
from py_ax12 import *
from ax12_preprogrammed_motion import *


# Setup GPIO pins 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)     # Control Data Direction Pin
# GPIO.setup(6,GPIO.OUT)      
# GPIO.setup(26,GPIO.OUT)

# LEDs on buttons 
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)
# print("LED on")
# GPIO.output(17,GPIO.LOW)
# GPIO.output(27,GPIO.LOW)
# sleep(1)
# print "LED off"
# GPIO.output(18,GPIO.LOW)

# Buttons
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# Motor IDs for each arm 
motor_right_h = 0x03
motor_left_h = 0x04
motor_right_v = 0x01
motor_left_v = 0x02
motors_right = [motor_right_h, motor_right_v]
motors_left = [motor_left_h, motor_left_v]


# HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65447      # Port to listen on (non-privileged ports are > 1023)


# Setup raspberry pi as server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.settimeout(0.2) # timeout for listening
server_socket.listen()

# Create serial object 
Dynamixel=serial.Serial("/dev/serial0",baudrate=1000000,timeout=0.1, bytesize=8)   # UART in ttyS0 @ 1Mbps


# Buffer for each arm to store last N servo position values 
buffer_length = 5
arr_right_h = list(np.full((buffer_length,), np.nan))
arr_left_h = list(np.full((buffer_length,), np.nan))
arr_right_v = list(np.full((buffer_length,), np.nan))
arr_left_v = list(np.full((buffer_length,), np.nan))
arr_right = [arr_right_h, arr_right_v]
arr_left = [arr_left_h, arr_left_v]

# Resolution of position hand-tracking 
# 'fine' or 'coarse'
tracking_resolution = 'fine'

# Resolution of position hand-tracking 
# 'autonomous' or 'teleoperated'
operating_mode = 'teleoperated'#'autonomous' #


def moving_average(new_val, arr, win_size):
    """ 
    Moving average filter 
    Returns average of last N values where N = window size
    """
    # Add the new value at start of list
    arr.insert(0, new_val)
    
    # Crop buffer to the correct length
    arr = arr[:win_size]
    print(arr)

    return np.nanmean(np.array(arr[:win_size]))


def hand_speed(arr):
    """ 
    Returns a value that increases with the difference 
    between the current and last recorded hand position
    """
    bias = 100                        # Minimum speed
    delta =  abs(arr[0] - arr[1])     # Difference between current and last position
    speed = delta * 3 + bias          # Equation to scale motor speed with hand speed
    if speed > 1023 : speed = 1023    # Cap maximum speed value
    if np.isnan(speed) : speed = bias # If difference is nan, use minimum speed
    return speed




while True:

    if GPIO.input(5) == GPIO.HIGH:
        print("Button 5 was pushed!")
        GPIO.output(17,GPIO.HIGH)
    else:
        GPIO.output(17,GPIO.LOW)


    if GPIO.input(6) == GPIO.HIGH:
        print("Button 6 was pushed!")
        GPIO.output(27,GPIO.HIGH)
    else:
        GPIO.output(27,GPIO.LOW)


    if operating_mode == 'teleoperated':

        try:

            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")

                while True:

                    if GPIO.input(5) == GPIO.HIGH:
                        print("Button 5 was pushed!")
                    else:
                        print("Button 5 not pushed!")


                    if GPIO.input(6) == GPIO.HIGH:
                        print("Button 6 was pushed!")

                    set_endless(0x03, False, Dynamixel)
                    set_endless(0x04, False, Dynamixel)
                    set_endless(0x02, False, Dynamixel)
                    set_endless(0x01, False, Dynamixel)
                    GPIO.output(18,GPIO.HIGH)

                    data = conn.recv(1024)
                    if not data:
                        break
                    msg = data.decode()
                    # print(msg)

                    if msg != 'no command' and msg != 'stop':

                        # Convert recieved string to nested list of x,y,z coordinates of each hand 
                        coordinates = msg.split(',')

                        # Convert string to floating point data 
                        coordinates = [float(i) for i in coordinates]

                        # Grouped coordintes 2D (x,y) or 3D (x,y,z) for each hand detected
                        n_dimensions = 3 # x,y,z coordinates recieved 
                        hands = [coordinates[i:i+n_dimensions] for i in range(0, len(coordinates), n_dimensions)]

                        # For each hand [left, right]
                        for hand, motors, arr, d in zip(hands, [motors_right, motors_left], [arr_right, arr_left], ['right', 'left']):

                            # Cap xy coordinates for each hand to between 0 and 1 
                            for i, j in enumerate(hand):
                                if hand[i]<=0: hand[i] = 0 
                                if hand[i]>=1: hand[i] = 1

                            print(d)
                            print('x pos ', hand[0])
                            print('y pos ', hand[1])

                            # convert to 10-bit value
                            # servo_position = (y_position * 1023) 
                            # hand = [1023 - h * 1023 for h in hand]

                            # map to full 10-bit range of possible servo positions
                            # hand[0] = hand[0] * 1023
                            # hand[1] = 1023 - hand[1] * 1023
                            # v_position = int(1023 - hand[1] * 1023)
                            # v_position = int((1 - hand[1]) * 1023)

                            # map horizontal motion to particular range 
                            min_in_L = 0
                            max_in_L = 0.75
                            min_in_R = 0.35
                            max_in_R = 1

                            min_out_L = 300#512
                            max_out_L = 1023
                            min_out_R = 0
                            max_out_R = 700#512

                            if d == 'right':
                                if hand[0]<=min_in_R: hand[0] = min_in_R
                                h_position = min_out_R + (max_out_R - min_out_R) * (hand[0]-min_in_R) / (max_in_R - min_in_R)
                            elif d == 'left': 
                                if hand[0]>=max_in_L: hand[0] = max_in_L
                                h_position = min_out_L + (max_out_L - min_out_L) * (hand[0]-min_in_L) / (max_in_L - min_in_L)

                            h_position = int(h_position)


                            # map vertical motion to particular range 
                            min_in_V = 0.25
                            max_in_V = 1
                            min_out_V = 0
                            max_out_V = 600

                            hand[1] = 1 - hand[1]
                            if hand[1]<=min_in_V: hand[1] = min_in_V
                            v_position = min_out_V + (max_out_V - min_out_V) * (hand[1]-min_in_V) / (max_in_V - min_in_V)
                            v_position = int(v_position)


                            if tracking_resolution == 'fine':

                                # Moving average filter applied, Position rounded to nearest decimal value
                                h_smoothed = int(moving_average(h_position, arr[0], buffer_length)) 
                                v_smoothed = int(moving_average(v_position, arr[1], buffer_length)) 

                                # Speed of hand in horizontal and vertical direction
                                h_speed = hand_speed(arr[0]) 
                                v_speed = hand_speed(arr[1])                  

                                # # Correct position to account for mirrored arrangement of servo arm mechanism 
                                # smoothed_position = 1023 - smoothed_position 

                                # Send 10-bit value to servos controlling horizontal and veritcal motion 
                                move_speed(motors[0], h_smoothed, h_speed, Dynamixel)
                                move_speed(motors[1], v_smoothed, v_speed, Dynamixel)
                                print('test motor commands are correct: str(motors)')
                                print('h= ', h_smoothed, ' v= ', v_smoothed)
                                print()

                            # tracking resolution is coarse
                            else: 
                                if v_position<0.35:
                                    print('up')
                                    move_speed(motors[0], 1023, 500, Dynamixel)
                                elif 0.35<=v_position<0.65:
                                    move_speed(motors[0], 512, 500, Dynamixel)
                                    print('mid')
                                else:
                                    move_speed(motors[0], 0, 500, Dynamixel)
                                    print('down')

                            


                    if msg == 'stop':
                        pass

                    elif msg == 'left':
                        move(0x04, 0, Dynamixel)
                        move(0x03, 0, Dynamixel)
                        move(0x02, 0, Dynamixel)
                        move(0x01, 0, Dynamixel)
                        sleep(0.1)

                    elif msg == 'right':
                        move(0x04, 150, Dynamixel)
                        move(0x03, 150, Dynamixel)
                        move(0x02, 150, Dynamixel)
                        move(0x01, 150, Dynamixel)
                        sleep(0.1)
                        

                    elif msg == 'forward':
                        pass

        except socket.timeout:
            pass

    else:

        while True:

            if GPIO.input(5) == GPIO.HIGH:
                print("Button 5 was pushed!")

            if GPIO.input(6) == GPIO.HIGH:
                print("Button 6 was pushed!")

            preprogrammed_motion(motor_right_v, 
                               motor_left_v, 
                               motor_right_h, 
                               motor_left_h)


