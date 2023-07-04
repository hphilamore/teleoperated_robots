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

 
left = 0x01
right = 0x02  
set_endless(left, False, Dynamixel)
set_endless(right, False, Dynamixel)


while True:

  GPIO.output(18,GPIO.HIGH)
  move_speed(left, 0, 20, Dynamixel)
  move_speed(right, 0, 20, Dynamixel)
  # i = move_check(0x04, 16)         
  sleep(1)
  move_speed(left, 150, 500, Dynamixel)
  move_speed(right, 150, 500, Dynamixel)
  # i = move_check(0x04, 544)  
  sleep(1)
  move(left, 512, Dynamixel)
  move(right, 512, Dynamixel)
  sleep(1)
  sweep(left, range(300), Dynamixel)
  sweep(left, range(300, 0, -1), Dynamixel)
  sweep(right, range(300), Dynamixel)
  sweep(right, range(300, 0, -1), Dynamixel)
  sweep(0x03, range(300), Dynamixel)
  sweep(0x03, range(300, 0, -1), Dynamixel)
  sweep(0x04, range(300), Dynamixel)
  sweep(0x04, range(300, 0, -1), Dynamixel)


