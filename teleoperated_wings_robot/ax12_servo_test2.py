import RPi.GPIO as GPIO
import serial
# import time
import os
from time import sleep
from time import time
from py_ax12 import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)     # Control Data Direction Pin
GPIO.setup(6,GPIO.OUT)      
GPIO.setup(26,GPIO.OUT)

# right = 0x01
# left = 0x02

# Create serial object 
Dynamixel=serial.Serial("/dev/serial0",baudrate=1000000,timeout=0.1, bytesize=8)   # UART in ttyS0 @ 1Mbps

 
left_v = 0x01
right_v = 0x02 
left_h = 0x03
right_h = 0x04 

set_endless(left_v, False, Dynamixel)
set_endless(right_v, False, Dynamixel)
set_endless(left_h, False, Dynamixel)
set_endless(right_h, False, Dynamixel)


while True:

  GPIO.output(18,GPIO.HIGH)
  # move_speed(left_h, 1024, 512, Dynamixel)
  # move_speed(right_h, 1024, 512, Dynamixel)
  # # i = move_check(0x04, 16)         
  # sleep(2)
  # move_speed(left_h, 0, 512, Dynamixel)
  # move_speed(right_h, 0, 512, Dynamixel)
  # # i = move_check(0x04, 544)  
  # sleep(2)
  move(left_h, 512, Dynamixel)
  move(right_h, 512, Dynamixel)
  move(left_v, 512, Dynamixel)
  move(right_v, 512, Dynamixel)
  sleep(2)
  sweep(left_v, range(1024), Dynamixel)
  sweep(left_v, range(1024, 0, -1), Dynamixel)
  sweep(right_v, range(1024), Dynamixel)
  sweep(right_v, range(1024, 0, -1), Dynamixel)
  sweep(left_h, range(1024), Dynamixel)
  sweep(left_h, range(1024, 0, -1), Dynamixel)
  sweep(right_h, range(1024), Dynamixel)
  sweep(right_h, range(1024, 0, -1), Dynamixel)
  sleep(2)


