import time
from dynamixel_sdk import *

# Control table addresses
ADDR_AX12_TORQUE_ENABLE = 24
ADDR_AX12_GOAL_POSITION = 30
ADDR_AX12_PRESENT_POSITION = 36
ADDR_AX12_MOVING_SPEED = 32

# Default settings
PROTOCOL_VERSION = 1.0  # Default AX-12 protocol version
BAUDRATE = 1000000  # Default baudrate of the Dynamixel AX-12 servo

# Dynamixel IDs
left_motor = 4  # ID of the first servo
right_motor = 3  # ID of the second servo

# Motors
motors = [left_motor, right_motor]

# Initialize the Dynamixel SDK
port_handler = PortHandler("/dev/serial0")
packet_handler = PacketHandler(PROTOCOL_VERSION)

def initialize_motors():
    # Open the port
    if not port_handler.openPort():
        print("Failed to open the port")
        return False

    # Set baudrate
    if not port_handler.setBaudRate(BAUDRATE):
        print("Failed to set the baudrate")
        return False

    # Enable torque all servos
    for motor in motors:
        dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, 
                                                                   motor, 
                                                                   ADDR_AX12_TORQUE_ENABLE, 1)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Failed to read present position for ID {motor}.")
            print(f"Error: {packet_handler.getTxRxResult(dxl_comm_result)}")
            return False

    return True

def set_goal_position(dxl_id, goal_pos, moving_speed):
    dxl_comm_result, dxl_error = packet_handler.write2ByteTxRx(port_handler, 
                                                               dxl_id, 
                                                               ADDR_AX12_GOAL_POSITION, 
                                                               goal_pos)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to read present position for ID {dxl_id}.")
        print(f"Error: {packet_handler.getTxRxResult(dxl_comm_result)}")
    
    packet_handler.write2ByteTxRx(port_handler, 
                                  dxl_id, 
                                  ADDR_AX12_MOVING_SPEED, 
                                  moving_speed)

def read_present_position(dxl_id):
    dxl_present_position, dxl_comm_result, dxl_error = packet_handler.read2ByteTxRx(port_handler, 
                                                                                    dxl_id, 
                                                                                    ADDR_AX12_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to read present position for ID {dxl_id}.")
        print(f"Error: {packet_handler.getTxRxResult(dxl_comm_result)}")
        return None
    return dxl_present_position

def main():
    # Initialize the motors
    if not initialize_motors():
        return

    # Set initial goal positions to 0 degrees and half moving speed
    set_goal_position(left_motor, 0, 512)
    set_goal_position(right_motor, 0, 512)

    # Wait for the servos to reach the initial positions
    time.sleep(2)

    # Sweep from 0 to 300 degrees
    for angle in range(0, 301, 10):
        set_goal_position(left_motor, angle, 512)
        set_goal_position(right_motor, angle, 512)
        time.sleep(0.1)

    # Read the final present positions
    pos1 = read_present_position(left_motor)
    pos2 = read_present_position(right_motor)
    print(f"Final positions - Servo 1: {pos1} degrees, Servo 2: {pos2} degrees")

    # Disable torque for both servos
    for motor in motors:
        packet_handler.write1ByteTxRx(port_handler, 
                                      motor, 
                                      ADDR_AX12_TORQUE_ENABLE, 
                                      0)
    
if __name__ == "__main__":
    main()
