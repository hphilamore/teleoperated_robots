import time
import RPi.GPIO as GPIO
import serial
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
AX12_1_ID = 3  # ID of the first servo
AX12_2_ID = 4  # ID of the second servo

# Raspberry Pi GPIO pins for serial communication
TX_PIN = 14  # GPIO 14 (BCM)
RX_PIN = 15  # GPIO 15 (BCM)

# USB-to-TTL converter serial port settings
SERIAL_PORT = "/dev/serial0"  # Replace with the appropriate port name
SERIAL_BAUDRATE = 57600  # Baudrate used in the tutorial (57600 bps)

# Initialize the Dynamixel SDK
port_handler = PortHandler(SERIAL_PORT)
packet_handler = PacketHandler(PROTOCOL_VERSION)

def initialize_motors():
    # Open the port
    if not port_handler.openPort():
        print("Failed to open the port")
        return False

    # Set baudrate
    if not port_handler.setBaudRate(SERIAL_BAUDRATE):
        print("Failed to set the baudrate")
        return False

    # Enable torque for both servos
    dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, AX12_1_ID, ADDR_AX12_TORQUE_ENABLE, 1)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to enable torque for ID {AX12_1_ID}. Error: {packet_handler.getTxRxResult(dxl_comm_result)}")
        return False

    dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, AX12_2_ID, ADDR_AX12_TORQUE_ENABLE, 1)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to enable torque for ID {AX12_2_ID}. Error: {packet_handler.getTxRxResult(dxl_comm_result)}")
        return False

    return True

def set_goal_position(dxl_id, goal_pos, moving_speed):
    dxl_comm_result, dxl_error = packet_handler.write2ByteTxRx(port_handler, dxl_id, ADDR_AX12_GOAL_POSITION, goal_pos)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to set goal position for ID {dxl_id}. Error: {packet_handler.getTxRxResult(dxl_comm_result)}")
    packet_handler.write2ByteTxRx(port_handler, dxl_id, ADDR_AX12_MOVING_SPEED, moving_speed)

def read_present_position(dxl_id):
    dxl_present_position, dxl_comm_result, dxl_error = packet_handler.read2ByteTxRx(port_handler, dxl_id, ADDR_AX12_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Failed to read present position for ID {dxl_id}. Error: {packet_handler.getTxRxResult(dxl_comm_result)}")
        return None
    return dxl_present_position

def main():
    # Setup GPIO pins for serial communication
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TX_PIN, GPIO.OUT)
    GPIO.setup(RX_PIN, GPIO.IN)
    GPIO.setup(18, GPIO.OUT)

    # Initialize the motors
    if not initialize_motors():
        return

    # Set initial goal positions to 0 degrees and half moving speed
    set_goal_position(AX12_1_ID, 0, 512)
    set_goal_position(AX12_2_ID, 0, 512)

    # Wait for the servos to reach the initial positions
    time.sleep(2)

    # Sweep from 0 to 300 degrees
    for angle in range(0, 301, 10):
        set_goal_position(AX12_1_ID, angle, 512)
        set_goal_position(AX12_2_ID, angle, 512)
        time.sleep(0.1)

    # Read the final present positions
    pos1 = read_present_position(AX12_1_ID)
    pos2 = read_present_position(AX12_2_ID)
    print(f"Final positions - Servo 1: {pos1} degrees, Servo 2: {pos2} degrees")

    # Disable torque for both servos
    packet_handler.write1ByteTxRx(port_handler, AX12_1_ID, ADDR_AX12_TORQUE_ENABLE, 0)
    packet_handler.write1ByteTxRx(port_handler, AX12_2_ID, ADDR_AX12_TORQUE_ENABLE, 0)

    # Cleanup GPIO pins
    GPIO.cleanup()

if __name__ == "__main__":
    main()
