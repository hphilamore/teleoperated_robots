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
tx_pin = 14
rx_pin = 15
enable_pin = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(enable_pin, GPIO.OUT)     # Control Data Direction Pin
GPIO.setup(tx_pin, GPIO.OUT)
GPIO.setup(rx_pin, GPIO.IN)
# GPIO.setup(6,GPIO.OUT)      
# GPIO.setup(26,GPIO.OUT)

# Motor IDs for each arm 
left_motor = 0x04
right_motor = 0x03


# HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65443      # Port to listen on (non-privileged ports are > 1023)


# Setup raspberry pi as server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.settimeout(0.2) # timeout for listening
server_socket.listen()
# server_socket.setblocking(False)

# Create serial object 
Dynamixel=serial.Serial("/dev/serial0",
                        baudrate=1000000,
                        timeout=0.1, 
                        bytesize=8)   # UART in ttyS0 @ 1Mbps

# All servos not continuous rotation
set_endless(0x03, False, Dynamixel)
set_endless(0x04, False, Dynamixel)
set_endless(0x02, False, Dynamixel)
set_endless(0x01, False, Dynamixel)

# # Enable servos 
# GPIO.output(enable_pin,GPIO.HIGH)


# Buffer for each arm to store last N servo position values 
buffer_length = 5
arr_left = list(np.full((buffer_length,), np.nan))
arr_right = list(np.full((buffer_length,), np.nan))

# Resolution of position hand-tracking 
# 'fine' or 'coarse'
tracking_resolution = 'coarse'


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
    print('speed_left', speed)
    return speed

def idle():
    print('no data recieved, idling')


def main():

    while True:
        try:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")

                while True:

                    # set_endless(0x03, False, Dynamixel)
                    # set_endless(0x04, False, Dynamixel)
                    # set_endless(0x02, False, Dynamixel)
                    # set_endless(0x01, False, Dynamixel)
                    
                    # Enable servos
                    GPIO.output(enable_pin,GPIO.HIGH)

                    data = conn.recv(1024)

                    # check if data received is empty
                    if not data:
                        idle()
                        break
                        

                    msg = data.decode()
                    # print(msg)

                    if msg != 'no command' and msg != 'stop':

                        coordinates = msg.split(',')

                        # Convert string to floating point data 
                        coordinates = [float(i) for i in coordinates]

                        # Grouped coordintes in x,y pairs for each hand detected
                        hands = [coordinates[i:i+2] for i in range(0, len(coordinates), 2)]

                        # print(coordinates)

                        # If 2 hands detected:
                        if len(hands) > 1:

                            # If x coordinate of both hands are on the same side of the screen, ignore one hand
                            if ((hands[0][0]<0.5 and hands[1][0]<0.5) or
                                (hands[0][0]>=0.5 and hands[1][0]>=0.5)):
                                hands = [hands[0]]

                        # For each hand 
                        for i in hands:

                            x_position = i[0]
                            y_position = i[1] 

                            print('y pos ', y_position)

                            # convert to 10-bit value
                            servo_position = (y_position * 1023) 

                            # Cap all negative values at 0
                            if servo_position<1: servo_position = 0 

                            # Convert floating point to integer
                            servo_position = int(servo_position)

                            # Hand x position on LEFT side of screen
                            if x_position<0.5:

                                if tracking_resolution == 'fine':

                                    # Moving average filter applied, Position rounded to nearest decimal value
                                    smoothed_position = int(moving_average(servo_position, arr_left, buffer_length)) 

                                    # Speed of hand
                                    speed = hand_speed(arr_left)                  

                                    # Correct position to account for mirrored arrangement of servo arm mechanism 
                                    smoothed_position = 1023 - smoothed_position 

                                    # Send 10-bit value to servo
                                    move_speed(left_motor, smoothed_position, speed, Dynamixel)

                                # tracking resolution is coarse
                                else: 
                                    # if y_position<0.5:
                                    #     # Send 10-bit value to servo
                                    #     move_speed(left_motor, 1023, 500, Dynamixel)
                                    # else:
                                    #     # Send 10-bit value to servo
                                    #     move_speed(left_motor, 0, 500, Dynamixel)
                                    if y_position<0.35:
                                        print('left up')
                                        move_speed(left_motor, 1023, 500, Dynamixel)
                                    elif 0.35<=y_position<0.65:
                                        move_speed(left_motor, 512, 500, Dynamixel)
                                        print('left mid')
                                    else:
                                        move_speed(left_motor, 0, 500, Dynamixel)
                                        print('left down')

                                
                            # Hand x position on RIGHT side of screen
                            if x_position>=0.5:

                                if tracking_resolution == 'fine':

                                    # Moving average filter applied, Position rounded to nearest decimal value
                                    smoothed_position = int(moving_average(servo_position, arr_right, buffer_length)) 

                                    # Speed of hand
                                    speed = hand_speed(arr_right)

                                    # smoothed_position = 1023 - smoothed_position 

                                    # Send 10-bit value to servo
                                    move_speed(right_motor, smoothed_position, speed, Dynamixel)

                                # tracking resolution is coarse
                                else: 
                                    # if y_position<0.5:
                                    #     # Send 10-bit value to servo
                                    #     move_speed(right_motor, 0, 500, Dynamixel)
                                    # else:
                                    #     # Send 10-bit value to servo
                                    #     move_speed(right_motor, 1023, 500, Dynamixel)
                                    if y_position<0.35:
                                        print('right up')
                                        move_speed(right_motor, 0, 500, Dynamixel)
                                    elif 0.35<=y_position<0.65:
                                        move_speed(right_motor, 512, 500, Dynamixel)
                                        print('right mid')
                                    else:
                                        move_speed(right_motor, 1023, 500, Dynamixel)
                                        print('right down')

                    # Keyboard arrow key controls 
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
            idle()
            pass

if __name__ == '__main__':
    main()


    # except BlockingIOError:
    #     print('waiting')
    #     pass



