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



def abortable_sleep(seconds, button):
   short_delay=0.001
   iterations = int(seconds/short_delay)
   for i in range(iterations):
      if button == GPIO.HIGH:
         break
      time.sleep(short_delay)

def preprogrammed_motion(motor_right_v, 
                         motor_left_v, 
                         motor_right_h, 
                         motor_left_h,
                         button
                         ):

  while button == GPIO.HIGH:

    GPIO.output(18,GPIO.HIGH)

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
      print('hello')
      move(motor_right_h, i, Dynamixel)
      move(motor_left_h, j, Dynamixel)
      abortable_sleep(0.003, button)
    abortable_sleep(0.1, button)

    # Move back 
    for i, j in zip(range(1023,0,-1), range(1023)):
      move(motor_right_h, i, Dynamixel)
      move(motor_left_h, j, Dynamixel)
      abortable_sleep(0.007, button)
    abortable_sleep(0.1, button)


    # Move forward asynchronous
    for i in range(500):
      move(motor_right_h, i, Dynamixel)
      abortable_sleep(0.005, button)

    for i, j in zip(range(501,1023), range(1023, 500, -1)):
      move(motor_right_h, i, Dynamixel)
      move(motor_left_h, j, Dynamixel)
      abortable_sleep(0.005, button)

    for j in range(500, 0, -1):
      move(motor_left_h, j, Dynamixel)
      abortable_sleep(0.005, button)


    # # Move back asynchronous 
    # for j in range(500):
    #   move(motor_left_h, j, Dynamixel)
    #   abortable_sleep(0.003, button)

    # for i, j in zip(range(1023, 500, -1), range(501,1023)):
    #   move(motor_right_h, i, Dynamixel)
    #   move(motor_left_h, j, Dynamixel)
    #   abortable_sleep(0.003, button)

    # for i in range(500, 0, -1):
    #   move(motor_right_h, i, Dynamixel)
    #   abortable_sleep(0.003, button)

    # # centre
    # for i, j in zip(range(0,512), range(1023, 512, -1)):
    #   move(motor_right_h, i, Dynamixel)
    #   move(motor_left_h, j, Dynamixel)
    #   abortable_sleep(0.006, button)

    # # lift
    # for i in range(0,512):
    #   move(motor_right_v, i, Dynamixel)
    #   move(motor_left_v, i, Dynamixel)
    #   abortable_sleep(0.006, button)

    # # lower
    # for i in range(512,0, -1):
    #   move(motor_right_v, i, Dynamixel)
    #   move(motor_left_v, i, Dynamixel)
    #   abortable_sleep(0.006, button)

    # # Move back 
    # for i, j in zip(range(512,0,-1), range(512, 1023)):
    #   move(motor_right_h, i, Dynamixel)
    #   move(motor_left_h, j, Dynamixel)
    #   abortable_sleep(0.010, button)
    # abortable_sleep(0.1, button)

    # # centre
    # for i, j in zip(range(0,512), range(1023, 512, -1)):
    #   move(motor_right_h, i, Dynamixel)
    #   move(motor_left_h, j, Dynamixel)
    #   abortable_sleep(0.005, button)
    # abortable_sleep(0.1, button)


    # # lift
    # for i in range(0,512):
    #   move(motor_right_v, i, Dynamixel)
    #   move(motor_left_v, i, Dynamixel)
    #   abortable_sleep(0.006, button)


    # # Move left
    # for i in range(512,300,-1):
    #   move(motor_right_h, i, Dynamixel)
    #   move(motor_left_h, i, Dynamixel)
    #   abortable_sleep(0.005, button)
    # abortable_sleep(0.1, button)

    # # Move right
    # for i in range(300, 1023):
    #   move(motor_right_h, i, Dynamixel)
    #   move(motor_left_h, i, Dynamixel)
    #   abortable_sleep(0.004, button)
    # abortable_sleep(0.1, button)


    # # lower
    # for i in range(512,0, -1):
    #   move(motor_right_v, i, Dynamixel)
    #   move(motor_left_v, i, Dynamixel)
    #   abortable_sleep(0.006, button)

    # # Move back 
    # for i in range(1023,0,-1):
    #   move(motor_right_h, i, Dynamixel)
    #   abortable_sleep(0.002, button)
    # abortable_sleep(0.1, button)


    print('done')
    abortable_sleep(1, button)


if __name__ == "__main__":
    while True:
      preprogrammed_motion(motor_right_v, 
                           motor_left_v, 
                           motor_right_h, 
                           motor_left_h,
                           button)


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


