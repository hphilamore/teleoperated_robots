import cv2
cams_test = 10
for i in range(0, cams_test):
    cap = cv2.VideoCapture(i)
    test, frame = cap.read()
    cv2.namedWindow('image',cv2.WINDOW_NORMAL)  
    cv2.imshow('image', frame)   
    print("i : "+str(i)+" /// result: "+str(test))
