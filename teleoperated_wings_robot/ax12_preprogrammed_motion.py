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



# Create serial object 
Dynamixel=serial.Serial("/dev/serial0",baudrate=1000000,timeout=0.1, bytesize=8)   # UART in ttyS0 @ 1Mbps

 
motor_right_v = 0x01
motor_left_v= 0x02 
motor_right_h = 0x03
motor_left_h = 0x04 

set_endless(motor_right_v, False, Dynamixel)
set_endless(motor_left_v, False, Dynamixel)
set_endless(motor_right_h, False, Dynamixel)
set_endless(motor_left_h, False, Dynamixel)

def preprogrammed_motion(motor_right_v, 
                         motor_left_v, 
                         motor_right_h, 
                         motor_left_h,
                         button):

  # while button == GPIO.HIGH:

  GPIO.output(18,GPIO.HIGH)

  GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  # sweep(motor_right_v, range(1023), 0.005, Dynamixel)
  # sweep(motor_right_v, range(1023, 0, -1), 0.005, Dynamixel)
  # sweep(right_v, range(1023), 0.005, Dynamixel)
  # sweep(right_v, range(1023, 0, -1), 0.005, Dynamixel)
  # sweep(motor_right_h, range(1023), 0.005, Dynamixel)
  # sweep(motor_right_h, range(1023, 0, -1), 0.01, Dynamixel)
  # sweep(motor_left_h, range(1023), 0.005, Dynamixel)
  # sweep(motor_left_h, range(1023, 0, -1), 0.01, Dynamixel)
  # sleep(3)

  # Move forward
  for i, j in zip(range(1023), range(1023,0,-1)):
    move(motor_right_h, i, Dynamixel)
    move(motor_left_h, j, Dynamixel)
    sleep(0.003)

  if not GPIO.input(button):
    print('exiting')
    return

  sleep(0.1)

  if not GPIO.input(button):
    print('exiting')
    return

  # Move back 
  for i, j in zip(range(1023,0,-1), range(1023)):
    move(motor_right_h, i, Dynamixel)
    move(motor_left_h, j, Dynamixel)
    sleep(0.007)

  if not GPIO.input(button):
    print('exiting')
    return

  sleep(0.1)

  if not GPIO.input(button):
    print('exiting')
    return

  # Move forward asynchronous
  for i in range(500):
    move(motor_right_h, i, Dynamixel)
    sleep(0.005)

  if not GPIO.input(button):
    print('exiting')
    return

  for i, j in zip(range(501,1023), range(1023, 500, -1)):
    move(motor_right_h, i, Dynamixel)
    move(motor_left_h, j, Dynamixel)
    sleep(0.005)

  if not GPIO.input(button):
    print('exiting')
    return

  for j in range(500, 0, -1):
    move(motor_left_h, j, Dynamixel)
    sleep(0.005)

  if not GPIO.input(button):
    print('exiting')
    return

  # Move back asynchronous 
  for j in range(500):
    move(motor_left_h, j, Dynamixel)
    sleep(0.003)

  if not GPIO.input(button):
    print('exiting')
    return

  for i, j in zip(range(1023, 500, -1), range(501,1023)):
    move(motor_right_h, i, Dynamixel)
    move(motor_left_h, j, Dynamixel)
    sleep(0.003)

  if not GPIO.input(button):
    print('exiting')
    return

  for i in range(500, 0, -1):
    move(motor_right_h, i, Dynamixel)
    sleep(0.003)

  if not GPIO.input(button):
    print('exiting')
    return

  # centre
  for i, j in zip(range(0,512), range(1023, 512, -1)):
    move(motor_right_h, i, Dynamixel)
    move(motor_left_h, j, Dynamixel)
    sleep(0.006)

  if not GPIO.input(button):
    print('exiting')
    return

  # lift
  for i in range(0,512):
    move(motor_right_v, i, Dynamixel)
    move(motor_left_v, i, Dynamixel)
    sleep(0.006)

  if not GPIO.input(button):
    print('exiting')
    return

  # lower
  for i in range(512,0, -1):
    move(motor_right_v, i, Dynamixel)
    move(motor_left_v, i, Dynamixel)
    sleep(0.006)

  if not GPIO.input(button):
    print('exiting')
    return

  # Move back 
  for i, j in zip(range(512,0,-1), range(512, 1023)):
    move(motor_right_h, i, Dynamixel)
    move(motor_left_h, j, Dynamixel)
    sleep(0.010)
  sleep(0.1)

  if not GPIO.input(button):
    print('exiting')
    return

  # centre
  for i, j in zip(range(0,512), range(1023, 512, -1)):
    move(motor_right_h, i, Dynamixel)
    move(motor_left_h, j, Dynamixel)
    sleep(0.005)

  if not GPIO.input(button):
    print('exiting')
    return

  sleep(0.1)

  if not GPIO.input(button):
    print('exiting')
    return

  # lift
  for i in range(0,512):
    move(motor_right_v, i, Dynamixel)
    move(motor_left_v, i, Dynamixel)
    sleep(0.006)

  if not GPIO.input(button):
    print('exiting')
    return

  # Move left
  for i in range(512,300,-1):
    move(motor_right_h, i, Dynamixel)
    move(motor_left_h, i, Dynamixel)
    sleep(0.005)

  if not GPIO.input(button):
    print('exiting')
    return

  sleep(0.1)

  if not GPIO.input(button):
    print('exiting')
    return

  # Move right
  for i in range(300, 1023):
    move(motor_right_h, i, Dynamixel)
    move(motor_left_h, i, Dynamixel)
    sleep(0.004)

  if not GPIO.input(button):
    print('exiting')
    return

  sleep(0.1)

  if not GPIO.input(button):
    print('exiting')
    return

  # lower
  for i in range(512,0, -1):
    move(motor_right_v, i, Dynamixel)
    move(motor_left_v, i, Dynamixel)
    sleep(0.006)

  if not GPIO.input(button):
    print('exiting')
    return

  # Move back 
  for i in range(1023,0,-1):
    move(motor_right_h, i, Dynamixel)
    sleep(0.002)

  if not GPIO.input(button):
    print('exiting')
    return

  sleep(0.1)

  if not GPIO.input(button):
    print('exiting')
    return

  print('done')
  sleep(1)


if __name__ == "__main__":
    # while True:
    preprogrammed_motion(motor_right_v, 
                         motor_left_v, 
                         motor_right_h, 
                         motor_left_h,
                         button=5)


  # for i, j in zip(range(1023,0,-1), range(1023)):
  #   move(motor_right_h, i, Dynamixel)
  #   move(motor_left_h, j, Dynamixel)
  #   sleep(0.002)
  # sleep(0.1)


  # move_speed(motor_right_h, 100, 512, Dynamixel)
  # move_speed(motor_left_h, 100, 512, Dynamixel)
  # move_speed(motor_right_v, 100, 512, Dynamixel)
  # move_speed(right_v, 100, 512, Dynamixel)
  # sleep(3)


