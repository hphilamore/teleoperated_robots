import cv2
import mediapipe
 
# Initialize MediaPipe solutions
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands

# Initialize VideoCapture
capture = cv2.VideoCapture(0)

# Initialize MediaPipe Pose
with handsModule.Hands(static_image_mode=False, 
                       min_detection_confidence=0.7, 
                       min_tracking_confidence=0.7, 
                       max_num_hands=2) as hands:
 
    while (True):
 
        # Read frame from video stream
        success, frame = capture.read()
        if not success:
            break

        # Convert the frame to RGB, Process the frame with MediaPipe Pose
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Check for hands
        if results.multi_hand_landmarks != None:

            # Draw hand landmarks onto the frame
            for handLandmarks in results.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame, 
                                             handLandmarks, 
                                             handsModule.HAND_CONNECTIONS)

            # Find each hand up to max number of hands 
            for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):
                print(f'HAND NUMBER: {hand_no+1}')
                print('-----------------------')
                # Find mean of x, y position of all nodes  
                x_ = []
                z_ = []

                for i in range(20):
                    x_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].x)
                    z_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].z)
                    
                # Find mean value of x and z coordinate of nodes 
                x = sum(x_)/len(x_)                
                z = sum(z_)/len(z_)

                print(x, z)

 
        cv2.imshow('Test hand', frame)
 
        if cv2.waitKey(1) == 27:
            break
 
cv2.destroyAllWindows()
capture.release()