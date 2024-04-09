import cv2
import mediapipe
import socket
import time
from mss import mss
import json
import platform
from transmitter import *


#--------------------------------""" SETUP """-----------------------------------------------
# TODO: Change to command line arguments 

# Source of input: 'camera' or 'window'
input_mode = 'camera' 

# Set to True to send command to raspberry pi
send_command = False

# The raspberry pi's hostname or IP address
HOST = "192.168.138.7"      

# The port used by the server
PORT = 65448               

#--------------------------------------------------------------------------------------------

# Detect computer operating system: 'Darwin' (Mac) or 'Windows'  
OS = platform.system()

# Windows-only module
if OS == 'Windows': 
    from screeninfo import get_monitors 



class VideoStreamTracker(Transmitter):

    def __init__(self,
                 send_command,
                 OS,  
                 HOST = "192.168.138.7", 
                 PORT = 65448,  
                 input_mode = 'camera',  # options: 'camera' or 'window'          
                 mirror_image = True,
                 input_window_fullscreen = False,
                 output_window_fullscreen = True,
                 show_wireframe = True,
                 window_name = 'Photo Booth:Photo Booth',
                 tracked_feature = 'body', # options: 'hands'/'body'
                 dual_camera_feed = False,
                 camera = 0,
                 ):
        
        super().__init__(HOST, PORT)

        # Source of input: 'leap_motion', 'camera' or 'window' or 'keys'
        self.input_mode = input_mode

        # Set to True to send command to raspberry pi
        self.send_command = send_command

        # Computer operating system: 'Darwin' (Mac) or 'Windows'  
        self.OS = OS

        # # The raspberry pi's hostname or IP address
        # self.HOST = HOST

        # # The port used by the server
        # self.port = PORT

        # Window name if using window
        # window_name = 'zoom.us'                      
        # window_name = 'Microsoft Teams'
        # window_name = 'zoom.us:Zoom Meeting'           # Find zoom meeting window 
        # window_name = 'zoom.us:zoom floating video'    # Find zoom meeting window during share screen ('pin' caller in zoom)
        # window_name = 'GoPro camera:'
        # window_name = 'Photo Booth:Photo Booth' 
        self.window_name = window_name
        # Set to True if source of video stream received will be full screeen 
        self.input_window_fullscreen = input_window_fullscreen

        # Set to True to make output video appear full screen
        self.output_window_fullscreen = output_window_fullscreen

        # Set to True to show wireframe in output video
        self.show_wireframe = show_wireframe

        # Nodes to track if taking image from camera or window: 'hands', 'body'
        self.tracked_feature = tracked_feature
        # track_hands_only = False

        # Set to true if image captured is a mirror of tracked person
        self.mirror_image = mirror_image

        # Take camera image from camera 0 or camera 1
        self.camera = camera

        """
        Dual camera feed
        Set to True if the computer running the client program has two camera feeds, for example if 
        a 360 camera for use in VR application is running to the same computer. 
        It is important that this flag is set to False if there is only one camera, as trying 
        to grab an image from a camera that isn't there will slow down the program significantly!
        """
        self.dual_camera_feed = dual_camera_feed

        # Setup web cam 0 (and web cam 1 if dual camera feed) ready for video capture 
        self.video_0 = cv2.VideoCapture(0)
        if self.dual_camera_feed:
            self.video_1 = cv2.VideoCapture(1)

        # Max number of hands to track
        self.n_hands = 2

        """
        Flag to indicate when no hand is deteced so that a timer can be set to 
        check of the person is really gone or if detection has failed momentarily 
        """
        self.flag_no_person_detected = False 

        # Number of seconds to wait until timeout  
        self.flag_timeout = 2 

        # Threshold distance between shoulders, below which person is too far away
        self.shoulder_distance_th = 0.1

        # Setup media pipe solutions 
        self.drawingModule = mediapipe.solutions.drawing_utils
        self.handsModule = mediapipe.solutions.hands
        self.mp_drawing = mediapipe.solutions.drawing_utils
        self.mp_pose = mediapipe.solutions.pose

        # Initialise variable to be sent to robot 
        self.command = {}


    def get_window_coordinates(self):
        """
        Returns coordinates of specified window name on desktop
        """
        process = Popen(['./windowlist', 'windowlist.m'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        window_positions = stdout.decode().split('\n')

        for w in window_positions:

            # Find window 
            if self.window_name in w:  

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

    def no_person_detected_timeout(self, flag_no_person_detected, flag_timeout):

        """
        Checks if there is no person in the frame or if detection has failed momentarily
        """

        if not flag_no_person_detected:     # If there was a hand in previous frame
            flag_no_person_detected = True  # Raise the flag 
            start = time.time()             # Start the timer
            print('no command (person not detected)') # Send the command to stop moving 
            self.command = 'no command'

        else:
            end = time.time()
            if end-start >= flag_timeout:           # If no person detected for time exceeding timeout 
                flag_no_person_detected = False     # Lower the flag 
                print('stop (person not detected)') # Send the command to stop moving 
                self.command = 'stop' 

        # return command

    def windows_output_fullscreen(self, frame):

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

    def format_for_transmission(self, pose_coordinates):

        """
        Formats data frame contianig node coordinates to send to robot
        """

        # Convert to json format (keys enclosed in double quotes)
        self.command = json.dumps(pose_coordinates)

        self.command = str(self.command)

        # # Convert to string to send to robot
        # return str(command)  

    # def send_command_to_server(self, HOST, PORT):
    #     """
    #     Uses sockets to send command to server robot over local network
    #     """
    #     # Send command to server socket on raspberry pi
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.connect((HOST, PORT))
    #         s.sendall(self.command.encode())

    def track_hands(self, frame, results, flag_no_person_detected, flag_timeout):

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
                x_, y_, z_ = [], [], []

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

                # Format coordinates to send to robot
                # command = self.format_for_transmission(pose_coordinates)
                self.format_for_transmission(pose_coordinates)

        else:
        #     command = self.no_person_detected_timeout(self.flag_no_person_detected, 
        #                                               self.flag_timeout)  
            self.no_person_detected_timeout(self.flag_no_person_detected, 
                                                      self.flag_timeout)  
        # return command

    def track_body(self, frame, results, flag_no_person_detected, flag_timeout):

        """
        Convert pose of body to robot command
        """

        # Draw the pose landmarks on the frame
        self.mp_drawing.draw_landmarks(frame, 
                                  results.pose_landmarks, 
                                  self.mp_pose.POSE_CONNECTIONS)

        # If a person is detected in the frame...
        if results.pose_landmarks:

            # Create a dictionary to store the coordinates of each node
            pose_coordinates = {}

            # Cycle through each node detected
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                
                # Nodes on human body to detect 
                if idx in [
                           self.mp_pose.PoseLandmark.NOSE.value,
                           self.mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                           self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                           # mp_pose.PoseLandmark.LEFT_ELBOW.value,
                           # mp_pose.PoseLandmark.RIGHT_ELBOW.value,
                           self.mp_pose.PoseLandmark.LEFT_WRIST.value,
                           self.mp_pose.PoseLandmark.RIGHT_WRIST.value,
                           self.mp_pose.PoseLandmark.LEFT_HIP.value,
                           self.mp_pose.PoseLandmark.RIGHT_HIP.value,
                           ]:

                    # Create array to store coodinates of individual node       
                    node_coordinates = []

                    # Get coordinates of node
                    x = landmark.x
                    y = landmark.y
                    z = landmark.z

                    for coordinate in [x,y,z]:

                        # Restrict value to within range (0, 1) 
                        if coordinate <= 0: coordinate = 0 
                        if coordinate >= 1: coordinate = 1 

                        # Round coordinate to 2 d.p. and store in array
                        node_coordinates.append(round(coordinate, 2))


                    # Get node name as a string
                    node_name = self.mp_pose.PoseLandmark(idx).name

                    # Add the coordinates to the dictionary using node name 
                    pose_coordinates[node_name] = node_coordinates


            # Swap left and right values if image captured is mirror of tracked person
            if self.mirror_image:          
                pose_coordinates["LEFT_HIP"], pose_coordinates["RIGHT_HIP"] = \
                pose_coordinates["RIGHT_HIP"], pose_coordinates["LEFT_HIP"]
                pose_coordinates["LEFT_WRIST"], pose_coordinates["RIGHT_WRIST"] = \
                pose_coordinates["RIGHT_WRIST"], pose_coordinates["LEFT_WRIST"]
                pose_coordinates["LEFT_SHOULDER"], pose_coordinates["RIGHT_SHOULDER"] = \
                pose_coordinates["RIGHT_SHOULDER"], pose_coordinates["LEFT_SHOULDER"]

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
            shoulder_distance = (pose_coordinates["LEFT_SHOULDER"][0] - \
                                 pose_coordinates["RIGHT_SHOULDER"][0]) 
            if shoulder_distance > self.shoulder_distance_th:
                print("Warning: Person detected but facing wrong way or too far away!")
                self.command = 'no command'
                       
            else:
                # Format coordinates to send to robot
                # command = self.format_for_transmission(pose_coordinates)
                self.format_for_transmission(pose_coordinates)

        else:
        #     command = self.no_person_detected_timeout(self.flag_no_person_detected, 
        #                                               self.flag_timeout)  
            self.no_person_detected_timeout(self.flag_no_person_detected, 
                                                      self.flag_timeout) 

        # return command

    def frame_from_window(self, window_coordinates):

        """
        Retrieves the current frame form the specified window
        """

        with mss() as sct:

            window = {"top": window_coordinates[1], 
                      "left": window_coordinates[0], 
                      "width": window_coordinates[3], 
                      "height": window_coordinates[2]
                   }

            # Grab current image    
            frame = np.array(sct.grab(window))

            # If full screen image grab required
            if self.input_window_fullscreen: 
                frame = np.array(ImageGrab.grab()) 

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            return frame

    def frame_from_camera(self, camera):
        """
        Retrieves the current frame form the specified camera
        """
        
        # Grab current image 
        ret0, frame0 = self.video_0.read()

        # Important to only grab second image if there are two cameras connected
        if self.dual_camera_feed:
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


    def track_video(self): 

        while(True):

            # --------------------------------
            # Set-up image processing model
            # --------------------------------

            if self.tracked_feature == 'hands':
                # Only hands tracked
                model = self.handsModule.Hands(static_image_mode=False, 
                                          min_detection_confidence=0.7, 
                                          min_tracking_confidence=0.7, 
                                          max_num_hands=n_hands)
            
            else:
                # Whole body tracked
                model = self.mp_pose.Pose(min_detection_confidence=0.5, 
                                     min_tracking_confidence=0.5,
                                    )
            # ------------------------------------
            # Get current frame from video feed
            # ------------------------------------
            with model as pose:

                # Frame taken from window
                if self.input_mode == 'window':
                    window_coordinates = self.get_window_coordinates()
                    frame = self.frame_from_window(window_coordinates)  
                    frame_copy  = self.frame_from_window(window_coordinates)    

                # Frame taken from camera
                else:
                    frame = self.frame_from_camera(self.camera)
                    frame_copy = self.frame_from_camera(self.camera)

                # -------------------------------------------------------------------------
                # Identify pose of tracked feature from frame and convert to robot command
                # -------------------------------------------------------------------------
                results = pose.process(frame)

                # ---------------------------------
                # Convert pose to robot command
                # ---------------------------------
                parameters = [frame, results, self.flag_no_person_detected, self.flag_timeout]

                # Hands tracked 
                if self.tracked_feature == 'hands':
                    # command = self.track_hands(*parameters) 
                    self.track_hands(*parameters) 

                # Body tracked
                else:
                    # command = self.track_body(*parameters)
                    self.track_body(*parameters)

                # ----------------------------------------------
                # Send command to server socket on raspberry pi
                # ----------------------------------------------
                if self.send_command:
                    # self.send_command_to_server(HOST, PORT)
                    self.send_command_to_server()

                # else:
                #     print(self.command)

                # ----------------------------------------------
                # Optionally show wireframe in output window
                # ----------------------------------------------  
                if self.show_wireframe:
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

                if self.OS == 'Windows': 
                    if self.output_window_fullscreen:
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

    video_tracker = VideoStreamTracker(send_command, OS, HOST, PORT)
    video_tracker.track_video()