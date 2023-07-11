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


# Setup GPIO pins 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)     # Control Data Direction Pin
GPIO.setup(6,GPIO.OUT)      
GPIO.setup(26,GPIO.OUT)

# Motor IDs for each arm 
motor_left_h = 0x03
motor_right_h = 0x04
motor_left_v = 0x01
motor_right_v = 0x02
motors_left = [motor_left_h, motor_left_v]
motors_right = [motor_right_h, motor_right_v]


# HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65445      # Port to listen on (non-privileged ports are > 1023)


# Setup raspberry pi as server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.settimeout(0.2) # timeout for listening
server_socket.listen()

# Create serial object 
Dynamixel=serial.Serial("/dev/serial0",baudrate=1000000,timeout=0.1, bytesize=8)   # UART in ttyS0 @ 1Mbps


# Buffer for each arm to store last N servo position values 
buffer_length = 5
arr_left_h = list(np.full((buffer_length,), np.nan))
arr_right_h = list(np.full((buffer_length,), np.nan))
arr_left_v = list(np.full((buffer_length,), np.nan))
arr_right_v = list(np.full((buffer_length,), np.nan))
arr_left = [arr_left_h, arr_left_v]
arr_right = [arr_right_h, arr_right_v]

# Resolution of position hand-tracking 
# 'fine' or 'coarse'
tracking_resolution = 'fine'


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
    try:

        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")

            while True:

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

                    # print(coordinates)

                    # If 2 hands detected:
                    # if len(hands) > 1:
                        # # If x coordinate of both hands are on the same side of the screen, ignore one hand
                        # if ((hands[0][0]<0.5 and hands[1][0]<0.5) or
                        #     (hands[0][0]>=0.5 and hands[1][0]>=0.5)):
                        #     hands = [hands[0]]

                    # For each hand [left, right]
                    for hand, motors, arr, d in zip(hands, [motors_left, motors_right], [arr_left, arr_right], ['left', 'right']):

                        # Cap xy coordinates for each hand to between 0 and 1 
                        for i, j in enumerate(hand):
                            
                            if hand[i]<=0: hand[i] = 0 
                            if hand[i]>=1: hand[i] = 1

                        # x_position = hand[0]
                        # y_position = hand[1] 

                        # # Cap all values to between 0 and 1 
                        # if x_position<=0: servo_position = 0 
                        # if servo_position>=1023: servo_position = 1023
                        print(d)
                        print('x pos ', hand[0])
                        print('y pos ', hand[1])

                        # convert to 10-bit value
                        # servo_position = (y_position * 1023) 
                        hand = [1023 - h * 1023 for h in hand]

                        # separate into x and y value (horizontal and vertical position) and convert to integer
                        h_position = int(hand[0])
                        v_position = int(hand[1])


                        # # Cap all values to between 0 and 1 
                        # if servo_position<=0: servo_position = 0 
                        # if servo_position>=1023: servo_position = 1023

                        # Convert floating point to integer
                        # servo_position = int(servo_position)

                        # Hand x position on LEFT side of screen
                        # if x_position<0.5:

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
                            # if y_position<0.5:
                            #     # Send 10-bit value to servo
                            #     move_speed(motor_left_h, 1023, 500, Dynamixel)
                            # else:
                            #     # Send 10-bit value to servo
                            #     move_speed(motor_left_h, 0, 500, Dynamixel)
                            if v_position<0.35:
                                print('up')
                                move_speed(motors[0], 1023, 500, Dynamixel)
                            elif 0.35<=v_position<0.65:
                                move_speed(motors[0], 512, 500, Dynamixel)
                                print('mid')
                            else:
                                move_speed(motors[0], 0, 500, Dynamixel)
                                print('down')

                            
                        # # Hand x position on RIGHT side of screen
                        # if x_position>=0.5:

                        #     if tracking_resolution == 'fine':

                        #         # Moving average filter applied, Position rounded to nearest decimal value
                        #         smoothed_position = int(moving_average(servo_position, arr_right_h, buffer_length)) 

                        #         # Speed of hand
                        #         speed = hand_speed(arr_right_h)

                        #         # smoothed_position = 1023 - smoothed_position 

                        #         # Send 10-bit value to servo
                        #         move_speed(right_motor_h, smoothed_position, speed, Dynamixel)

                        #     # tracking resolution is coarse
                        #     else: 
                        #         # if y_position<0.5:
                        #         #     # Send 10-bit value to servo
                        #         #     move_speed(right_motor_h, 0, 500, Dynamixel)
                        #         # else:
                        #         #     # Send 10-bit value to servo
                        #         #     move_speed(right_motor_h, 1023, 500, Dynamixel)
                        #         if y_position<0.35:
                        #             print('right up')
                        #             move_speed(right_motor_h, 0, 500, Dynamixel)
                        #         elif 0.35<=y_position<0.65:
                        #             move_speed(right_motor_h, 512, 500, Dynamixel)
                        #             print('right mid')
                        #         else:
                        #             move_speed(right_motor_h, 1023, 500, Dynamixel)
                        #             print('right down')

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
    


