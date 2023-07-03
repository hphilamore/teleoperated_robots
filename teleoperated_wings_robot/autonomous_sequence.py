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

# Motor IDs for each arm 
left_h_motor = 0x04
right_h_motor = 0x03
left_v_motor = 0x02
right_v_motor = 0x01


# Create serial object 
Dynamixel=serial.Serial("/dev/serial0",
                        baudrate=1000000,
                        timeout=0.1, 
                        bytesize=8)   # UART in ttyS0 @ 1Mbps


# All servos not continuous rotation
# set_endless(0x03, False, Dynamixel)
# set_endless(0x04, False, Dynamixel)
set_endless(0x02, False, Dynamixel)
set_endless(0x01, False, Dynamixel)

while True:


    GPIO.output(enable_pin, GPIO.HIGH)
    # move_speed(0x01, 0, 20, Dynamixel)
    # move_speed(0x02, 0, 20, Dynamixel)
    # # i = move_check(0x04, 16)         
    # sleep(1)
    # move_speed(0x01, 150, 500, Dynamixel)
    # move_speed(0x02, 150, 500, Dynamixel)
    # # i = move_check(0x04, 544)  
    # sleep(1)
    # move(0x01, 512, Dynamixel)
    # move(0x02, 512, Dynamixel)
    # sleep(1)
    sweep(right_v_motor, range(300), Dynamixel)
    sweep(right_v_motor, range(300, 0, -1), Dynamixel)
    # sweep(0x02, range(300), Dynamixel)
    # sweep(0x02, range(300, 0, -1), Dynamixel)
    # sweep(0x03, range(300), Dynamixel)
    # sweep(0x03, range(300, 0, -1), Dynamixel)
    # sweep(0x04, range(300), Dynamixel)
    # sweep(0x04, range(300, 0, -1), Dynamixel)

    # # Enable servos 
    # GPIO.output(enable_pin, GPIO.HIGH)

    # move_speed(left_h_motor, 1024, 1024, Dynamixel)
    # move_speed(right_h_motor, 1024, 1024, Dynamixel)
    # sleep(1)
    # move_speed(left_h_motor, 0, 1024, Dynamixel)
    # move_speed(right_h_motor, 0, 1024, Dynamixel)
    # sleep(2)

    # move_speed(left_h_motor, 1024, 512, Dynamixel)
    # sleep(0.5)
    # move_speed(right_h_motor, 1024, 512, Dynamixel)
    # sleep(0.5)
    # move_speed(left_h_motor, 0, 512, Dynamixel)
    # sleep(0.5)
    # move_speed(right_h_motor, 0, 512, Dynamixel)
    # sleep(2)

    # move_speed(left_h_motor, 1024, 512, Dynamixel)
    # sleep(0.5)
    # move_speed(right_h_motor, 1024, 512, Dynamixel)
    # sleep(0.5)
    # move_speed(left_h_motor, 0, 512, Dynamixel)
    # sleep(0.5)
    # move_speed(right_h_motor, 0, 512, Dynamixel)
    # sleep(0.5)
    # move_speed(right_h_motor, 1024, 512, Dynamixel)
    # sleep(2)

    # sweep(left_h_motor, range(50,250), 200, serial_object)
    # sweep(right_h_motor, range(1024,512,-1), 200, serial_object)






