import mediapipe as mp
import cv2

# Initialize MediaPipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Initialize Videocapture
capture = cv2.VideoCapture(0)

# Initialize MediaPipe Pose
with mp_pose.Pose(min_detection_confidence=0.5, 
                  min_tracking_confidence=0.5) as pose:

    while capture.isOpened():

        # Read frame from video stream
        success, frame = capture.read()
        if not success:
            break

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)



        # Process the frame with MediaPipe Pose
        results = pose.process(frame_rgb)

        # Draw the pose landmarks on the frame
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Extract and print the XYZ coordinates of shoulders, elbows, knees, wrists, and hands
        if results.pose_landmarks:
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                if idx in [
                           # mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                           # mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                           # mp_pose.PoseLandmark.LEFT_ELBOW.value,
                           # mp_pose.PoseLandmark.RIGHT_ELBOW.value,
                           mp_pose.PoseLandmark.LEFT_WRIST.value,
                           mp_pose.PoseLandmark.RIGHT_WRIST.value,
                           # mp_pose.PoseLandmark.LEFT_KNEE.value,
                           # mp_pose.PoseLandmark.RIGHT_KNEE.value
                           ]:
                    x = landmark.x
                    y = landmark.y
                    z = landmark.z
                    print(f"Person {idx // 33 + 1}, Point {mp_pose.PoseLandmark(idx).name}: X={x}, Y={y}, Z={z}")

        # Display the resulting frame
        cv2.imshow('MediaPipe Pose', frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if cv2.waitKey(1) == 27:
            break

# Release resources
capture.release()
cv2.destroyAllWindows()
