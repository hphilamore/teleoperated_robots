#!/usr/bin/env python3
# https://realpython.com/python-sockets/
# https://www.explainingcomputers.com/rasp_pi_robotics.html

"""
#----------------------------------------------------------

Tracks hand position in image from web-cam. 

Chooses a command based on hand position.

Sends command to raspberry pi robot over wifi. 

#----------------------------------------------------------
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

#-------------------------------------------------------------------------------
""" SETUP """

HOST = "192.168.145.223" # 1.14"#56.103"#7"#103"  # The raspberry pi's hostname or IP address
PORT = 65447           # The port used by the server

# Take video stream from 'camera' or 'window' or 'keys'
input_mode = 'camera'#'keys' #'window' ###'keys'#'camera' ##'camera'##'camera'  

# Window name is using window
win_name = 'zoom.us'                      
#win_name = 'Microsoft Teams'
win_name = 'zoom.us:Zoom Meeting'          # Find zoom meeting window 
#win_name = 'zoom.us:zoom floating video'  # Find zoom meeting window during share screen ('pin' caller in zoom)
#win_name = 'Vysor'                        # Find vysor window for robot POV 
#win_name = 'Vysor:SM'                     # Find vysor window for robot POV 
#win_name = 'Vysor:ART'                    # Find vysor window for robot POV 
win_name = 'Photo Booth:Photo Booth' 
# win_name = 'GoPro Webcam:'  

# Choose OC as macOS or windowsOS 
OS = 'macOS' #'windowsOS'

# Set as True if the image to run hand tracking on is full screeen 
grab_full_screen_image = False

# Output video appears full screen if True
make_output_window_fullscreen = True

# Show wireframe in output video
show_wireframe = True

# Send command to raspberry pi
send_command = False

# Max number of hands to track (wings: track 2 hands, turtle robots: track 1 hand)
n_hands = 2

# Detail of hands tracked when True, otherwise whole body frame 
track_hands_only = False

# Swap left and right values if image captured is mirror of tracked person
mirror_nodes = True

# Take camera image from webcam 0 or webcam 1
which_camera = 0

# Set to True if the computer running the lcient program has two camera feeds in 
dual_camera_feed = False

#-------------------------------------------------------------------------------
# A flag to indicate when no hand is deteced so that a timer can be set to 
# check of the person is really gone or if detection has failed momentarily 
flag_no_person_detected = False 
# Number of seconds to wait until timeout  
flag_timeout = 2 

if OS == 'windowsOS': 
    from screeninfo import get_monitors # windows only
 
# Setup media pipe solutions 
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
mp_drawing = mediapipe.solutions.drawing_utils
mp_pose = mediapipe.solutions.pose

# Setup web cam 0 and web cam 1, ready for video capture 
capture0 = cv2.VideoCapture(0)
if dual_camera_feed:
    capture1 = cv2.VideoCapture(1)


def window_coordinates():
    process = Popen(['./windowlist', 'windowlist.m'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    window_positions = stdout.decode().split('\n')

    for w in window_positions:
        # Find window 
        if win_name in w:                        
            # Separate window info 
            w = w.split(':')                     
            # Separate window coordinates
            coordinates = w[-1].split(',')       
            # Convert coordinates to integer
            coordinates = [int(float(i)) for i in coordinates] 
            break
    else:
        print("No window with specified name")
        print("Exiting program...")
        sys.exit(1)  

    return coordinates

def calculate_average_depth(person):
    # Calculate the average depth coordinate across all landmarks
    depth_sum = sum([landmark.z for landmark in person.landmark])
    average_depth = depth_sum / len(person.landmark)
    return average_depth

def track_hands(frame, pose, flag_no_person_detected, flag_timeout):
    results = pose.process(frame)

    # If hands detected in the frame
    if results.multi_hand_landmarks != None:

        # Draw landmarks onto frame
        for handLandmarks in results.multi_hand_landmarks:
            drawingModule.draw_landmarks(frame, 
                                         handLandmarks, 
                                         handsModule.HAND_CONNECTIONS)

        # # A list to store the x,y,z coordinates of each hand 
        # pose_coordinates = []
        # A dictionary to store the x,y,z coordinates of each node
        pose_coordinates = {}

        # Cyle through each hand detected 
        for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):
            print(f'HAND NUMBER: {hand_no+1}')
            print('-----------------------')

            # Array to store all nodes on each hand 
            x_ = []
            y_ = []
            z_ = []

            # 20 nodes per hand 
            for i in range(20):
                x_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].x)
                y_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].y)
                z_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].z)
                    
            # Find mean value of nodes on each hand, to 2 d.p., to treat as single node per hand   
            x = round(sum(x_)/len(x_), 2)                
            y = round(sum(y_)/len(y_), 2)                
            z = round(sum(z_)/len(z_), 2)

            node = [x,y,z]

            # Cap x,y,z, coordinates for each hand to between 0 and 1 
            for dimension in node:
                if dimension <= 0: dimension = 0 
                if dimension >= 1: dimension = 1 

            # Store hand node in dictionary 
            pose_coordinates['HAND' + str(hand_no+1)] = node

            # Convert to json format (keys enclosed in double quotes)
            command = pose_coordinates
            command = json.dumps(command)

            # Convert to string to send to robot
            command = str(command)

    else:
        print('No hand detected')
        if not flag_no_person_detected:     # If there was a hand in previous frame
            flag_no_person_detected = True  # Raise the flag 
            start = time.time()             # Start the timer
            command = 'no command'

        else:
            end = time.time()
            if end-start >= flag_timeout:
                flag_no_person_detected = False  # Lower the flag 
                print('stop')
                command = 'stop'  

    return command

def track_body(frame, pose, flag_no_person_detected, flag_timeout):
    # Process the frame with MediaPipe Pose
    results = pose.process(frame)

    # Draw the pose landmarks on the frame
    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # if a person is detected in the frame...
    if results.pose_landmarks:

        # a dictionary to store the x,y,z coordinates of each node
        pose_coordinates = {}

        # cycle through each node detected
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            
            # nodes on human body to detect 
            if idx in [
                       mp_pose.PoseLandmark.NOSE.value,
                       mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                       mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                       # mp_pose.PoseLandmark.LEFT_ELBOW.value,
                       # mp_pose.PoseLandmark.RIGHT_ELBOW.value,
                       mp_pose.PoseLandmark.LEFT_WRIST.value,
                       mp_pose.PoseLandmark.RIGHT_WRIST.value,
                       mp_pose.PoseLandmark.LEFT_HIP.value,
                       mp_pose.PoseLandmark.RIGHT_HIP.value,
                       ]:

                # array to store coodinates of individual node       
                node_coordinates = []

                x = landmark.x
                y = landmark.y
                z = landmark.z

                # restrict value of each coordinate to within range (0, 1) 
                for coordinate in [x,y,z]:
                    if coordinate <= 0: coordinate = 0 
                    if coordinate >= 1: coordinate = 1 

                    # round coordinate to 2 d.p. and store in array
                    node_coordinates.append(round(coordinate, 2))

                # floor divide landmark index by 33 to get a unique index for each person 
                # (each person has 33 landmarks)
                print(f"Person {idx // 33}")
                print(f"Point {mp_pose.PoseLandmark(idx).name}:")
                print(f"X={round(x,2)}, Y={round(y,2)}, Z={round(z,2)}")
                node_name = mp_pose.PoseLandmark(idx).name
                pose_coordinates[node_name] = node_coordinates


        # Swap left and right values if image captured is mirror of tracked person
        if mirror_nodes:
            pose_coordinates["LEFT_HIP"], pose_coordinates["RIGHT_HIP"] = pose_coordinates["RIGHT_HIP"], pose_coordinates["LEFT_HIP"]
            pose_coordinates["LEFT_WRIST"], pose_coordinates["RIGHT_WRIST"] = pose_coordinates["RIGHT_WRIST"], pose_coordinates["LEFT_WRIST"]
            pose_coordinates["LEFT_SHOULDER"], pose_coordinates["RIGHT_SHOULDER"] = pose_coordinates["RIGHT_SHOULDER"], pose_coordinates["LEFT_SHOULDER"]


        # Don't send pose if person far from camera (i.e. distance between shoulders too small) 
        # or if person facing away from camera (i.e. right shoulder has greater x position than left shoulder) 
        if (pose_coordinates["RIGHT_SHOULDER"][0]-pose_coordinates["LEFT_SHOULDER"][0]) < 0.1:
            print(pose_coordinates["RIGHT_SHOULDER"][0]-pose_coordinates["LEFT_SHOULDER"][0])
            print("Warning: Person detected but not close enough to screen!")
            command = 'no command'

        # Otherwise send dictionary as description of pose         
        else:
            # Convert to json format (keys enclosed in double quotes)
            command = pose_coordinates
            command = json.dumps(command)
        
        # Convert to string to send to robot
        command = str(command)



    else:
        print('No person detected')
        if not flag_no_person_detected:     # If there was a hand in previous frame
            flag_no_person_detected = True  # Raise the flag 
            start = time.time()  # Start the timer
            command = 'no command'

        else:
            end = time.time()
            if end-start >= flag_timeout:
                flag_no_person_detected = False  # Lower the flag 
                print('stop')
                command = 'stop' 

    return command



def frame_from_window(window_coordinates):
    with mss() as sct:

        window = {"top": window_coordinates[1], 
                  "left": window_coordinates[0], 
                  "width": window_coordinates[3], 
                  "height": window_coordinates[2]
               }

        # Grab current image    
        frame = np.array(sct.grab(window))

        # If full screen image grab required
        if grab_full_screen_image: 
            frame = np.array(ImageGrab.grab()) 

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        return frame

def frame_from_camera(capture):
    # Grab current image 
    ret0, frame0 = capture0.read()
    if dual_camera_feed:
        ret1, frame1 = capture1.read()

    # Take image from selected camera
    if which_camera == 0:
    	frame = frame0
    else:
    	frame = frame1

    # Modify colours
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Flip image
    frame = cv2.flip(frame, 1)
    return frame


def show_tracked_wireframe(frame, OS):
    if OS == 'windowsOS': 
        if make_output_window_fullscreen:

            # To make output window full screen:
            for monitor in get_monitors():
                screen_h = monitor.height
                screen_w = monitor.width
            
            frame_h, frame_w, _ = frame.shape

            scaleWidth = float(screen_w)/float(frame_w)
            scaleHeight = float(screen_h)/float(frame_h)

            if scaleHeight>scaleWidth:
                imgScale = scaleWidth
            else:
                imgScale = scaleHeight

            newX,newY = frame_w*imgScale, frame_h*imgScale

            cv2.namedWindow('image',cv2.WINDOW_NORMAL)      # Implicitly create the window
            cv2.resizeWindow('image', int(newX),int(newY))  # Resize the window


    try:
        cv2.imshow('image', frame)                 # Show the window 
        
    except:
        pass


def send_command_to_server(HOST, PORT):
    # Send command to server socket on raspberry pi
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of address
        s.connect((HOST, PORT))
        s.sendall(command.encode())




if input_mode == 'keys':

    screen = curses.initscr()
    curses.noecho() 
    curses.cbreak()
    screen.keypad(True)

    command = 'stop'

    try:

        while(True):
            char = screen.getch()

            if char == ord('q'):
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
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of address
                s.connect((HOST, PORT))
                s.sendall(command.encode())
                # data = s.recv(1024)

    except KeyboardInterrupt:
        #Close down curses properly, inc turn echo back on!
        curses.nocbreak(); screen.keypad(0); curses.echo()
        curses.endwin()
        sys.exit(1)


elif input_mode == 'window':
    # Set up window for image capture
    window_coordinates = window_coordinates()
     

elif input_mode == 'camera':
    """ Setup web cam ready for video capture """
    capture = cv2.VideoCapture(0)
 

while(True):

    if track_hands_only:
        model = handsModule.Hands(static_image_mode=False, 
                                  min_detection_confidence=0.7, 
                                  min_tracking_confidence=0.7, 
                                  max_num_hands=n_hands)
    else:
        model = mp_pose.Pose(min_detection_confidence=0.5, 
                             min_tracking_confidence=0.5,
                            )

    with model as pose:

        # Input taken from window
        if input_mode == 'window':
            frame = frame_from_window(window_coordinates)  
            frame_copy  = frame_from_window(window_coordinates)    

        elif input_mode == 'camera':
            frame = frame_from_camera(capture)
            frame_copy = frame_from_camera(capture)


        # Look for hands 
        if track_hands_only:
            command = track_hands(frame, pose, flag_no_person_detected, flag_timeout) 
        else:
            command = track_body(frame, pose, flag_no_person_detected, flag_timeout)

        print('command ', command)

        # Visualise output
        if show_wireframe:
            show_tracked_wireframe(frame, OS) 
        else:
            show_tracked_wireframe(frame_copy, OS) 
 
        if cv2.waitKey(1) == 27:
            break

        if send_command:
            send_command_to_server(HOST, PORT)
