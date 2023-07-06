import cv2
import mediapipe
from mss import mss
import sys
from subprocess import Popen, PIPE
import numpy as np


def track_hand_coordinates_setup(OS, input_mode):

	"""
	param: OS: 'windowsOS', ''
	param: input_mode: 'window', 'camera'
	"""


	if OS == 'windowsOS': 
		from screeninfo import get_monitors # windows only
 
	# Set up mediapipe solutions 
	drawingModule = mediapipe.solutions.drawing_utils
	handsModule = mediapipe.solutions.hands

	# A flag to indicate when no hand is deteced so that a timer can be set to 
	# check of the hand is really gone or if detection has failed momentarily 
	flag_no_hand = False 

	# Setup web cam ready for video capture 
	capture = cv2.VideoCapture(0)


	if input_mode == 'window':
	    """ Set up window for image capture """ 
	    process = Popen(['./windowlist', 'windowlist.m'], stdout=PIPE, stderr=PIPE)
	    stdout, stderr = process.communicate()
	    window_positions = stdout.decode().split('\n')

	    for w in window_positions:
	        if win_name in w:                        # Find window 
	            print(w)
	            w = w.split(':')                     # Separate window info 
	            print(w)
	            coordinates = w[-1].split(',')       # Separate window coordinates
	            print(coordinates)
	            coordinates = [int(float(i)) for i in coordinates]  # Convert coordinates to integer
	            print(coordinates)

	elif input_mode == 'camera':
	    """ Setup web cam ready for video capture """
	    capture = cv2.VideoCapture(0)

	
def track_hand_coordinates(OS, input_mode):

	"""
	param: OS: 'windowsOS', ''
	param: input_mode: 'window', 'camera'
	"""

	with handsModule.Hands(static_image_mode=False, 
	                   min_detection_confidence=0.7, 
	                   min_tracking_confidence=0.7, 
	                   max_num_hands=n_hands) as hands:


	    # with mss() as sct:
	        
	    """
	    Input taken from window
	    """
	    if input_mode == 'window':

	        with mss() as sct:

	            try:
	                # Use coordinates of window
	                # with mss() as sct:
	                window = {"top": coordinates[1], 
	                      "left": coordinates[0], 
	                      "width": coordinates[3], 
	                      "height": coordinates[2]
	                       }

	                # Grab current image    
	                frame = np.array(sct.grab(window))

	                # If full screen image grab required
	                if grab_full_screen_image: 
	                    frame = np.array(ImageGrab.grab()) 

	                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

	            except:
	                print("No window with specified name")
	                print("Exiting program...")
	                sys.exit(1)
	        

	    elif input_mode == 'camera':
	        """
	        Input taken from webcam
	        """
	        ret, frame = capture.read()
	        # Grab current image    
	        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	        frame = cv2.flip(frame, 1)


	    # Look for hands    
	    results = hands.process(frame)

	    # Check for hands
	    if results.multi_hand_landmarks != None:

	        # Draw hands
	        for handLandmarks in results.multi_hand_landmarks:
	            drawingModule.draw_landmarks(frame, 
	                                         handLandmarks, 
	                                         handsModule.HAND_CONNECTIONS)

	        hand_coordinates = []

	        # Find each hand up to max number of hands 
	        for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):
	            print(f'HAND NUMBER: {hand_no+1}')
	            print('-----------------------')

	            x_ = []
	            y_ = []
	            z_ = []

	            for i in range(20):
	                x_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].x)
	                y_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].y)
	                z_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].z)
	                    
	            # Find mean value of x and z coordinate of nodes 
	            x = sum(x_)/len(x_)                
	            y = sum(y_)/len(y_)                
	            z = sum(z_)/len(z_)

	            print(x, y, z)

	            # Add the mean values to the list of coordinates to send to raspberry pi
	            hand_coordinates.append(str(round(x, 2)))
	            hand_coordinates.append(str(round(y, 2)))

	        # Choose a command to send to the raspberry pi robot 
	        # command = pos_to_command(x, y, z)
	        command = ','.join(hand_coordinates)
	        print(command)

	    else:
	            print('no hand')
	            if not flag_no_hand:     # If there was a hand in previous frame
	                flag_no_hand = True  # Raise the flag 
	                start = time.time()  # Start the timer
	                command = 'no command'

	            else:
	                end = time.time()
	                if end-start >= 3:
	                    flag_no_hand = False  # Lower the flag 
	                    print('stop')
	                    command = 'stop'  


	    # if send_command:
	    #     # Send command to server socket on raspberry pi
	    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	    #         # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of address
	    #         s.connect((HOST, PORT))
	    #         s.sendall(command.encode())


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

	    # if cv2.waitKey(1) == 27:
	    #     break

	return command