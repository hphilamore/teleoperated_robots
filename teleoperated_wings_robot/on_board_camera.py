# Connecting rapsberry pi to arduino using i2c
#https://www.deviceplus.com/arduino/connecting-a-raspberry-pi-to-an-arduino-uno/
#https://www.deviceplus.com/arduino/using-i2c-and-an-arduino-uno-to-work-with-analogue-voltages-on-a-raspberry-pi/

import cv2
import mediapipe
import RPi.GPIO as GPIO
import serial
import time


N_hands = 1 # maximum number of hands to detect 

# TODO: work out how to change serial0--> AMA0 on RPi
# TODO: set serial permissions on RPi so that 'sudo su' not required to acess ttyS0 to run programme
# https://roboticsbackend.com/raspberry-pi-hardware-permissions/
# TODO: add set-up stuff to README on repo 
Dynamixel=serial.Serial("/dev/serial0",baudrate=1000000,timeout=0.1, bytesize=8)   # UART in ttyS0 @ 1Mbps

 
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
 
capture = cv2.VideoCapture(0)

frameWidth = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
frameHeight = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)


with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=N_hands) as hands:

    while True:

        ret, frame = capture.read()
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
 
        if results.multi_hand_landmarks != None:
            #print('hand detected - ', end='')
            for handLandmarks in results.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame, handLandmarks, handsModule.HAND_CONNECTIONS)
 
            for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):
                print('-----------------------')

                x_ = []
                z_ = []

                for i in range(20):
                    x_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].x)
                    z_.append(hand_landmarks.landmark[handsModule.HandLandmark(i).value].z)
                    
                x = sum(x_)/len(x_)                
                z = sum(z_)/len(z_)
    
                print()
                print(f'x = {x}')
                print(f'z = {z}')
                
        else:                          
            
            print('no hand')
            turn(left, cw, 0)
            turn(right, ccw, 0) 
                
        
        # comment out for set-up without display e.g/ headless raspberry pi
        try:
            cv2.imshow('Test hand', frame)
        except:
            pass
 
        if cv2.waitKey(1) == 27:
            break
 
cv2.destroyAllWindows()
capture.release()