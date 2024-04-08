#!/usr/bin/env python3
# https://realpython.com/python-sockets/
# https://www.explainingcomputers.com/rasp_pi_robotics.html

"""

Tracks motion of human body from video feed OR keyboard strokes 

Sends command to raspberry pi robot over wifi (body coordinates or command for each key stroke)

"""
import cv2
import mediapipe
import socket
import time
from mss import mss
import sys
from subprocess import Popen, PIPE
import numpy as np
import curses
import json
import leap
import platform
from leap_motion_tracking import *
from video_stream_tracking import *

#--------------------------------""" SETUP """-----------------------------------------------
# TODO: Change to command line arguments 

HOST = "192.168.0.53"      # The raspberry pi's hostname or IP address
PORT = 65448               # The port used by the server

# Source of input: 'leap_motion', 'camera' or 'window' or 'keys'
input_mode = 'camera'#'leap_motion'#'camera'#'window'#'leap_motion'# 'camera' ##'camera'#'keys' 

# Set to True to send command to raspberry pi
send_command = False

#--------------------------------------------------------------------------------------------

# Detect computer operating system: 'Darwin' (Mac) or 'Windows'  
OS = platform.system()

# Windows-only module

if OS == 'Windows': 
    from screeninfo import get_monitors 

def track_keys():

    """
    Tracks keystrokes typed in terminal and converts to commands
    """

    # Set up terminal to track keys
    screen = curses.initscr()
    curses.noecho() 
    curses.cbreak()
    screen.keypad(True)


    # Default command to send 
    command = 'stop'

    try:

        while(True):

            # Get last typed character
            char = screen.getch()


            if char == ord('q'):
                print("quit")
                break

            elif char == curses.KEY_UP:
                print("up")
                command = 'forward'

            elif char == curses.KEY_DOWN:
                print("down")
                command = 'backward'

            elif char == curses.KEY_RIGHT:
                print("right")
                command = 'right'

            elif char == curses.KEY_LEFT:
                print("left")
                command = 'left'

            elif char == ord('s'): #10:
                print("stop")
                command = 'stop' 

            # Send command to server socket on raspberry pi
            send_command_to_server(HOST, PORT, command)
            # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #     s.connect((HOST, PORT))
            #     s.sendall(command.encode())

    except KeyboardInterrupt:
        #Close down curses properly, inc turn echo back on!
        curses.nocbreak(); screen.keypad(0); curses.echo()
        curses.endwin()
        sys.exit(1)

def track_leap_motion():
    leap_motion_tracker = LeapMotionTracker()

    connection = leap.Connection()
    connection.add_listener(leap_motion_tracker)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)

        while running:

            # If no hand detected, stop robot
            leap_motion_tracker.command = 'stop'
            print(leap_motion_tracker.command)

            # Send command to robot 
            if send_command:
                send_command_to_server(HOST, PORT, leap_motion_tracker.command)

            time.sleep(1)


if __name__ == "__main__":


    if input_mode == 'keys':
        track_keys()

    elif input_mode == 'leap_motion':
        print('LEAP')
        track_leap_motion()

    else:
        video_tracker = VideoStreamTracker(input_mode, send_command, OS)
        video_tracker.track_video()


