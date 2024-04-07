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
import time

#-------------------------------------------------------------------------------
""" SETUP """


HOST = "192.168.0.52"      # The raspberry pi's hostname or IP address
PORT = 65448               # The port used by the server

# Source of video stream: 'camera' or 'window' or 'keys'
input_mode = 'leap_motion'#'camera'#'keys' #'window' ###'keys'#'camera' ##'camera'##'camera'  

# Window name if using window
# window_name = 'zoom.us'                      
# window_name = 'Microsoft Teams'
# window_name = 'zoom.us:Zoom Meeting'          # Find zoom meeting window 
# window_name = 'zoom.us:zoom floating video'    # Find zoom meeting window during share screen ('pin' caller in zoom)
# window_name = 'GoPro camera:'
window_name = 'Photo Booth:Photo Booth' 
  

# Computer operating system: 'macOS' or 'windowsOS'  
OS = 'macOS' #'windowsOS'

# Set to True if source of video stream will be full screeen 
grab_full_screen_image = False

# Set to True to make output video appears full screen
make_output_window_fullscreen = True

# Set to True to show wireframe in output video
show_wireframe = True

# Set to True to send command to raspberry pi
send_command = False

# Max number of hands to track
n_hands = 2

# Nodes to track: 'hands', 'body'
tracked_feature = 'body'
# track_hands_only = False

# Set to true if image captured is a mirror of tracked person
mirror_image = True

"""
Set to True if the computer running the client program has two camera feeds, for example if 
a 360 camera for use in VR application is running to the same computer. 
It is important that this flag is set to False if there is only one camera, as trying 
to grab an image from a camera that isn't there will slow down the program significantly!
"""
dual_camera_feed = False

# Take camera image from camera 0 or camera 1
camera = 0


#-------------------------------------------------------------------------------
"""
Flag to indicate when no hand is deteced so that a timer can be set to 
check of the person is really gone or if detection has failed momentarily 
"""
flag_no_person_detected = False 
# Number of seconds to wait until timeout  
flag_timeout = 2 

# Windows-only module
if OS == 'windowsOS': 
    from screeninfo import get_monitors # windows only
 
# Setup media pipe solutions 
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
mp_drawing = mediapipe.solutions.drawing_utils
mp_pose = mediapipe.solutions.pose

# Setup web cam 0 (and web cam 1 if dual camera feed) ready for video capture 
video_0 = cv2.VideoCapture(0)
if dual_camera_feed:
    video_1 = cv2.VideoCapture(1)

# Threshold distance between shoulders, below which person is too far away
shoulder_distance_th = 0.1

def window_coordinates():
    """
    Returns coordinates of specified window name on desktop
    """
    process = Popen(['./windowlist', 'windowlist.m'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    window_positions = stdout.decode().split('\n')

    for w in window_positions:

        # Find window 
        if window_name in w:  

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

def no_person_detected_timeout(flag_no_person_detected, flag_timeout):

    """
    Checks if there is no person in the frame or if detection has failed momentarily
    """

    if not flag_no_person_detected:     # If there was a hand in previous frame
        flag_no_person_detected = True  # Raise the flag 
        start = time.time()             # Start the timer
        print('no command (person not detected)') # Send the command to stop moving 
        command = 'no command'

    else:
        end = time.time()
        if end-start >= flag_timeout:           # If no person detected for time exceeding timeout 
            flag_no_person_detected = False     # Lower the flag 
            print('stop (person not detected)') # Send the command to stop moving 
            command = 'stop' 

    return command


def windows_output_fullscreen(frame):

    """
    Make output window full screen on windows OS
    """

    # Get screen width and height
    for monitor in get_monitors():
        screen_h = monitor.height
        screen_w = monitor.width
    
    # Get frame width and height
    frame_h, frame_w, _ = frame.shape

    # Get scaling factors
    scaleWidth = float(screen_w)/float(frame_w)
    scaleHeight = float(screen_h)/float(frame_h)

    # Choose smaller of two scaling factors
    if scaleHeight>scaleWidth:
        imgScale = scaleWidth
    else:
        imgScale = scaleHeight

    # Get output window dimensions
    newX,newY = frame_w*imgScale, frame_h*imgScale

    # Implicitly create the window
    cv2.namedWindow('image',cv2.WINDOW_NORMAL)

    # Resize the window        
    cv2.resizeWindow('image', int(newX),int(newY))  


def track_hands(frame, results, flag_no_person_detected, flag_timeout):

    """
    Convert pose of hands to robot command
    """

    # If hands detected in the frame
    if results.multi_hand_landmarks != None:

        # Draw landmarks onto frame
        for handLandmarks in results.multi_hand_landmarks:
            drawingModule.draw_landmarks(frame, 
                                         handLandmarks, 
                                         handsModule.HAND_CONNECTIONS)

        # A data structure to store the x,y,z coordinates of each node
        pose_coordinates = {}

        # Cyle through each hand detected 
        for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):
            print(f'HAND NUMBER: {hand_no+1}')
            print('-----------------------')

            # Create arrays to store coordinates all nodes on each hand 
            x_ = []
            y_ = []
            z_ = []

            # 20 nodes per hand 
            for i in range(20):
                x_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].x)
                y_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].y)
                z_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].z)
                    
            # Find hand centroid as mean value of nodes on each hand  
            x = round(sum(x_)/len(x_), 2)                
            y = round(sum(y_)/len(y_), 2)                
            z = round(sum(z_)/len(z_), 2)

            # Use centroid as single hand node
            node = [x,y,z]

            # Restrict value of each coordinate to within range (0, 1) 
            for dimension in node:
                if dimension <= 0: dimension = 0 
                if dimension >= 1: dimension = 1 

            # Store node for each hand in dictionary 
            pose_coordinates['HAND' + str(hand_no+1)] = node

            # Convert to json format (keys enclosed in double quotes)
            command = pose_coordinates
            command = json.dumps(command)

            # Convert to string to send to robot
            command = str(command)

    else:
        command = no_person_detected_timeout(flag_no_person_detected, flag_timeout)  

    return command

def track_body(frame, results, flag_no_person_detected, flag_timeout):

    """
    Convert pose of body to robot command
    """

    # Draw the pose landmarks on the frame
    mp_drawing.draw_landmarks(frame, 
                              results.pose_landmarks, 
                              mp_pose.POSE_CONNECTIONS)

    # If a person is detected in the frame...
    if results.pose_landmarks:

        # Create a dictionary to store the coordinates of each node
        pose_coordinates = {}

        # Cycle through each node detected
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            
            # Nodes on human body to detect 
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

                # Create array to store coodinates of individual node       
                node_coordinates = []

                # Get coordinates of node
                x = landmark.x
                y = landmark.y
                z = landmark.z

                # Restrict value of each coordinate to within range (0, 1) 
                for coordinate in [x,y,z]:
                    if coordinate <= 0: coordinate = 0 
                    if coordinate >= 1: coordinate = 1 

                    # Round coordinate to 2 d.p. and store in array
                    node_coordinates.append(round(coordinate, 2))


                # Get node name as a string
                node_name = mp_pose.PoseLandmark(idx).name

                # Add the coordinates to the dictionary using node name 
                pose_coordinates[node_name] = node_coordinates


        # Swap left and right values if image captured is mirror of tracked person
        if mirror_image:          
            pose_coordinates["LEFT_HIP"], pose_coordinates["RIGHT_HIP"] = pose_coordinates["RIGHT_HIP"], pose_coordinates["LEFT_HIP"]
            pose_coordinates["LEFT_WRIST"], pose_coordinates["RIGHT_WRIST"] = pose_coordinates["RIGHT_WRIST"], pose_coordinates["LEFT_WRIST"]
            pose_coordinates["LEFT_SHOULDER"], pose_coordinates["RIGHT_SHOULDER"] = pose_coordinates["RIGHT_SHOULDER"], pose_coordinates["LEFT_SHOULDER"]

        for node_name, coordinates in pose_coordinates.items():
            if node_name == 'NOSE':
                node_name += '\t'
            print(node_name, '\t', coordinates)

        """
        Detect if:
        - person too far from camera 
          (i.e. distance between shoulders too small) 
        - person facing away from camera 
          (i.e. right shoulder has greater x position than left shoulder) 
        And don't send command to robot 
        """
        shoulder_distance = (pose_coordinates["LEFT_SHOULDER"][0] - pose_coordinates["RIGHT_SHOULDER"][0]) 
        if shoulder_distance > shoulder_distance_th:
            print("Warning: Person detected but facing wrong way or too far away!")
            command = 'no command'
            
        # Otherwise, send dictionary of coorinates of nodes         
        else:
            # Convert to json format (keys enclosed in double quotes)
            command = pose_coordinates
            command = json.dumps(command)
            # Convert to string to send to robot
            command = str(command)  

    else:
        # Check if there is no person in the frame or if detection has failed momentarily
        command = no_person_detected_timeout(flag_no_person_detected, flag_timeout) 

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

def frame_from_camera(camera):
    
    # Grab current image 
    ret0, frame0 = video_0.read()

    # Important to only grab second image if there are two cameras connected
    if dual_camera_feed:
        ret1, frame1 = video_1.read()

    # Take image from selected camera
    if camera == 0:
        frame = frame0
    else:
        frame = frame1

    # Modify colours
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Flip image
    frame = cv2.flip(frame, 1)
    return frame

def send_command_to_server(HOST, PORT, command):
    # Send command to server socket on raspberry pi
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(command.encode())

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


def track_video():

    # Input mode is window
    if input_mode == 'window':
        # Set up window for image capture
        window_coordinates = window_coordinates()
         
    # # Input mode is camera
    # else:
    #     # Setup camera ready for video capture
    #     capture = cv2.VideoCapture(0)
 

    while(True):

        # --------------------------------
        # Set-up image processing model
        # --------------------------------

        if tracked_feature == 'hands':
            # Only hands tracked
            model = handsModule.Hands(static_image_mode=False, 
                                      min_detection_confidence=0.7, 
                                      min_tracking_confidence=0.7, 
                                      max_num_hands=n_hands)
        
        else:
            # Whole body tracked
            model = mp_pose.Pose(min_detection_confidence=0.5, 
                                 min_tracking_confidence=0.5,
                                )
        # ------------------------------------
        # Get current frame from video feed
        # ------------------------------------
        with model as pose:

            # Frame taken from window
            if input_mode == 'window':
                frame = frame_from_window(window_coordinates)  
                frame_copy  = frame_from_window(window_coordinates)    

            # Frame taken from camera
            else:
                frame = frame_from_camera(camera)
                frame_copy = frame_from_camera(camera)

            # -------------------------------------------------------------------------
            # Identify pose of tracked feature from frame and convert to robot command
            # -------------------------------------------------------------------------
            results = pose.process(frame)

            # ---------------------------------
            # Convert pose to robot command
            # ---------------------------------
            parameters = [frame, results, flag_no_person_detected, flag_timeout]
            # Hands tracked 
            if tracked_feature == 'hands':
                command = track_hands(*parameters) 

            # Body tracked
            else:
                command = track_body(*parameters)

            # print('command ', command)

            # ----------------------------------------------
            # Send command to server socket on raspberry pi
            # ----------------------------------------------
            if send_command:
                send_command_to_server(HOST, PORT, command)

            # ----------------------------------------------
            # Optionally show wireframe in output window
            # ----------------------------------------------  
            if show_wireframe:
                pass
            else:
                frame = frame_copy

            # ----------------------------------------------
            # Setup output window
            # ----------------------------------------------
            # Implicitly create the window
            cv2.namedWindow('image',cv2.WINDOW_NORMAL) 

            # Resize the window
            cv2.resizeWindow('image', 600, 400)        

            # ----------------------------------------------
            # Make output window full screen on windows OS
            # ----------------------------------------------
            if OS == 'windowsOS': 
                if make_output_window_fullscreen:
                    windows_output_fullscreen(frame)

            # ----------------------------------------------
            # Show the outut image 
            # ----------------------------------------------    
            try:
                cv2.imshow('image', frame)                 # Show the window 
            except:
                pass
    
            # This line needed to display video feed 
            if cv2.waitKey(1) == 27:
                break


if __name__ == "__main__":

    if input_mode == 'keys':
        track_keys()

    elif input_mode == 'leap_motion':
        print('LEAP')

    else:
        track_video()


