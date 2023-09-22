#!/usr/bin/env python3

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


# Set as True to discretise vertical servo posotion to up/down/mid instead of following hand
coarse_servo_v_position = False


# Setup GPIO pins 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
enable_pin = 18
GPIO.setup(enable_pin,GPIO.OUT)     # Control Data Direction Pin


# LEDs on buttons 
teleop_mode_LED = 17
preprog_mode_LED = 27
GPIO.setup(teleop_mode_LED ,GPIO.OUT)
GPIO.setup(preprog_mode_LED,GPIO.OUT)

# Buttons
teleop_mode_button = 5
preprog_mode_button = 6
GPIO.setup(teleop_mode_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(preprog_mode_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# Motor IDs for each arm 
motor_right_h = 0x03
motor_left_h = 0x04
motor_right_v = 0x01
motor_left_v = 0x02
motors_right = [motor_right_h, motor_right_v]
motors_left = [motor_left_h, motor_left_v]


# HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 65451      # Port to listen on (non-privileged ports are > 1023)


# Setup raspberry pi as server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.settimeout(0.2) # timeout for listening
server_socket.listen()

# Create serial object 
Dynamixel=serial.Serial("/dev/serial0",baudrate=1000000,timeout=0.1, bytesize=8)   # UART in ttyS0 @ 1Mbps


# Buffer for each arm to store last N servo position values 
buffer_length = 5
buffer_right_h = list(np.full((buffer_length,), np.nan))
buffer_left_h = list(np.full((buffer_length,), np.nan))
buffer_right_v = list(np.full((buffer_length,), np.nan))
buffer_left_v = list(np.full((buffer_length,), np.nan))
buffer_right = [buffer_right_h, buffer_right_v]
buffer_left = [buffer_left_h, buffer_left_v]
# Indexing of horizontal and vertical direction
h = 0
v = 1

# Resolution of position hand-tracking 
# 'fine' or 'coarse'
tracking_resolution = 'fine'

# Indexing of xyz coordinates
x = 0
y = 1
z = 2



def moving_average(new_val, buffer, win_size=buffer_length):
    """ 
    Moving average filter 
    Returns average of last N values where N = window size
    """
    # Add the new value at start of list
    buffer.insert(0, new_val)
    
    # Crop buffer to the correct length
    buffer = buffer[:win_size]
    print(buffer)

    return np.nanmean(np.array(buffer[:win_size]))


def hand_speed(buffer):
    """ 
    Returns a value that increases with the difference 
    between the current and last recorded hand position
    """
    bias = 100                        # Minimum speed
    delta =  abs(buffer[0] - buffer[1])     # Difference between current and last position
    speed = delta * 3 + bias          # Equation to scale motor speed with hand speed
    if speed > 1023 : speed = 1023    # Cap maximum speed value
    if np.isnan(speed) : speed = bias # If difference is nan, use minimum speed
    return speed


# Loop forever checking for mode button press and/or connection by remote client  
while True:

    # # Teleoperated mode button pressed
    # if (GPIO.input(teleop_mode_button) == GPIO.HIGH and 
    #     GPIO.input(preprog_mode_button) == GPIO.LOW):
    #     print("Teleoperated")
    #     # Turn button pressed LED on and other LED off
    #     GPIO.output(teleop_mode_LED,GPIO.HIGH)
    #     GPIO.output(preprog_mode_LED,GPIO.LOW)

    # Listen for message from client 
    try:
        conn, addr = server_socket.accept()
        with conn:
            # print(f"Connected by {addr}")

            # Teleoperated mode button pressed
            while (GPIO.input(teleop_mode_button) == GPIO.HIGH and 
                   GPIO.input(preprog_mode_button) == GPIO.LOW):

                print("Teleoperated Mode")

                # Turn button pressed LED on and other LED off
                GPIO.output(teleop_mode_LED,GPIO.HIGH)
                GPIO.output(preprog_mode_LED,GPIO.LOW)

                set_endless(0x03, False, Dynamixel)
                set_endless(0x04, False, Dynamixel)
                set_endless(0x02, False, Dynamixel)
                set_endless(0x01, False, Dynamixel)
                GPIO.output(18,GPIO.HIGH)

                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode()

                if msg not in ['no command', 'stop', 'forward', 'backward', 'right', 'left']:

                    # convert string-dictionary of node coordinates to dictionary
                    msg = json.loads(msg)

                    print('msg2', type(msg), msg)

                    # array to store x,y,z coordinates for each hand  
                    hands = ["RIGHT_WRIST", "LEFT_WRIST"]

                    # For each hand [left, right]
                    for hand, motors, buffer, side in zip(hands, 
                                                       [motors_right, motors_left], 
                                                       [buffer_right, buffer_left]):
                        
                        x_pos = msg[hand][x]
                        y_pos = msg[hand][y]

                        print('x pos ', x_pos)
                        print('y pos ', y_pos)

                        # Input range for horizontal position of left and right hand 
                        # (absolute min=0, absolute max=1)
                        min_in_L = 0
                        max_in_L = 0.75
                        min_in_R = 0.35
                        max_in_R = 1

                        # Input range for vertical position of left and right hand 
                        # (absolute min=0, absolute max=1)
                        min_in_L = 0
                        max_in_L = 0.75
                        min_in_R = 0.35
                        max_in_R = 1

                        # Output range for horizontal position servos 
                        # (absolute min=0, absolute max=1023)
                        min_out_L = 300#512
                        max_out_L = 1023
                        min_out_R = 0
                        max_out_R = 700#512

                        # Output range for vertical position servos 
                        # (absolute min=0, absolute max=1023)
                        min_in_V = 0.25
                        max_in_V = 1
                        min_out_V = 0
                        max_out_V = 600

                        # Map horizontal pose to servos  
                        if side == 'right':
                            if x_pos<=min_in_R: x_pos = min_in_R
                            h_position = (min_out_R + (max_out_R - min_out_R) * (x_pos-min_in_R) / 
                                         (max_in_R - min_in_R))
                        elif side == 'left': 
                            if x_pos>=max_in_L: x_pos = max_in_L
                            h_position = (min_out_L + (max_out_L - min_out_L) * (x_pos-min_in_L) / 
                                         (max_in_L - min_in_L))

                        h_position = int(h_position)

                        # Map vertical pose to servos 
                        y_pos = 1 - y_pos # Correct position to account for mirrored servo arrangement
                        if y_pos<=min_in_V: y_pos = min_in_V
                        v_position = (min_out_V + (max_out_V - min_out_V) * (y_pos-min_in_V) / 
                                     (max_in_V - min_in_V))
                        v_position = int(v_position)

                        # Moving average filter applied, Position rounded to nearest decimal value
                        h_smoothed = int(moving_average(new_val=h_position, buffer=buffer[h])) 
                        v_smoothed = int(moving_average(new_val=v_position, buffer=buffer[v])) 

                        # Scale speed of servo to speed of hand in horizontal and vertical direction
                        h_speed = hand_speed(buffer[h]) 
                        v_speed = hand_speed(buffer[v])                  

                        # Send 10-bit value to servos controlling horizontal and veritcal motion 
                        move_speed(motors[0], h_smoothed, h_speed, Dynamixel)
                        move_speed(motors[1], v_smoothed, v_speed, Dynamixel)
                        print('h_servo= ', h_smoothed, ' v_servo= ', v_smoothed)
                        print()

                        # Servo control resolution is coarse
                        if coarse_servo_v_position:
                            if v_smoothed<0.35:
                                print('up')
                                move_speed(motors[0], 1023, 500, Dynamixel)
                            elif 0.35<=v_smoothed<0.65:
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

    # No message from client 
    except socket.timeout:
        pass

    # # Autonomous mode button pressed
    # elif (GPIO.input(preprog_mode_button) == GPIO.HIGH and 
    #       GPIO.input(teleop_mode_button) == GPIO.LOW):
    #     print("Autonomous mode")
    #     # Turn button pressed LED on and other LED off
    #     GPIO.output(teleop_mode_LED,GPIO.LOW)
    #     GPIO.output(preprog_mode_LED,GPIO.HIGH)

    # Autonomous mode 
    while(GPIO.input(preprog_mode_button) == GPIO.HIGH and 
          GPIO.input(teleop_mode_button) == GPIO.LOW):

        print("Autonomous mode")

        # Turn button pressed LED on and other LED off
        GPIO.output(teleop_mode_LED,GPIO.LOW)
        GPIO.output(preprog_mode_LED,GPIO.HIGH)

        preprogrammed_motion(motor_right_v, 
                             motor_left_v, 
                             motor_right_h, 
                             motor_left_h)

    # Both teleoperated and Autonomous mode button pressed
    while (GPIO.input(preprog_mode_button) == GPIO.HIGH and 
          GPIO.input(teleop_mode_button) == GPIO.HIGH):
        # Turn both LEDs on
        GPIO.output(teleop_mode_LED,GPIO.HIGH)
        GPIO.output(preprog_mode_LED,GPIO.HIGH)


    # No button pressed
    # Turn both LEDs off
    GPIO.output(teleop_mode_LED,GPIO.LOW)
    GPIO.output(preprog_mode_LED,GPIO.LOW)

