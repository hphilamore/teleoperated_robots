
import leap
import time
import cv2
from transmitter import *


#--------------------------------""" SETUP """-----------------------------------------------
# TODO: Change to command line arguments 

# Set to True to send command to raspberry pi
send_command = False

# The raspberry pi's hostname or IP address
HOST = "192.168.138.7"      

# The port used by the server
PORT = 65448               

#--------------------------------------------------------------------------------------------

class LeapMotionTracker(leap.Listener, Transmitter):

    def __init__(self,
                 send_command,
                 HOST = "192.168.138.7", 
                 PORT = 65448
                 ):

        leap.Listener.__init__(self)
        Transmitter.__init__(self, HOST, PORT)
        
        self.send_command = send_command
        self.command = 'stop'

    def on_connection_event(self, event):
        print("Connected")

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def hand_coordinates_to_command(self, pose_coordinates):
        # TODO: Cusrrent bug, comparing lists. Need to compare coordiates values! 

        """
        Converts hand pose coordinates to robot commands 
        """

        # Set a threshold indicating the midpoint of the horizontal and vertical range 
        vertical_th = 220
        horizontal_th = 0

        # Default command to send 
        self.command = 'no command'

        # Initialize arrays to store coordinates of each hand 
        left, right = [], []

        # Replace with recievd coordinates 
        try:
            left = pose_coordinates["LEFT_HAND"]
        except:
            pass

        try:
            right = pose_coordinates["RIGHT_HAND"]
        except:
            pass

        print('left', left)
        print('right', right)

        # If less than 2 hands can be seen, stop the robot 
        if left == [] and right == []:
            self.command = 'stop'

        # If both hands left, turn left     
        elif left==[] and right!=[]:
            self.command = 'right'

        elif right==[] and left!=[]:
            self.command = 'left'

        elif left[1] > vertical_th and right[1] > vertical_th:
            self.command = 'forward'

        elif left[1] < vertical_th and right[1] < vertical_th:
            self.command = 'backward'

        print(self.command)

    def on_tracking_event(self, event):
        """
        Code to run whenever a hand is detected 
        """
        pose_coordinates = {}

        for hand in event.hands:
            pose_coordinates[str(hand.type).upper()[9:] + "_HAND"] = [round(hand.palm.position.x, 2),
                                                                      round(hand.palm.position.y, 2),
                                                                      round(hand.palm.position.z, 2)
                                                                     ]

            for node_name, coordinates in pose_coordinates.items():
                print(node_name, '\t', coordinates)

            self.hand_coordinates_to_command(pose_coordinates)

            if self.send_command:
                # self.send_command_to_server(HOST, PORT)
                self.send_command_to_server()

            else:
                print(self.command)

    def idling(self):

        # If no hand detected, stop robot
        self.command = 'stop'
        print(self.command)

        if self.send_command:
            # self.send_command_to_server(HOST, PORT)
            self.send_command_to_server()

        time.sleep(1)


def track_leap_motion():
    leap_motion_tracker = LeapMotionTracker(send_command, HOST, PORT)

    connection = leap.Connection()
    connection.add_listener(leap_motion_tracker)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)

        while running:

            leap_motion_tracker.idling()


if __name__ == "__main__":

    track_leap_motion()