import serial
import time
import RPi.GPIO as GPIO

# Serial port settings
SERIAL_PORT = "/dev/serial0"  # Replace with the appropriate port name
BAUDRATE = 1000000  # Baudrate used in the tutorial (57600 bps)

# Setup GPIO pins 
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.OUT)     # Control Data Direction Pin
tx_pin = 14
rx_pin = 15
GPIO.setup(tx_pin, GPIO.OUT)
GPIO.setup(rx_pin, GPIO.IN)

def read_servo_position(servo_id):
    # Open the serial port
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, , tx=tx_pin, rx=rx_pin)

    # Construct the instruction packet
    packet = bytearray([0xFF, 0xFF, servo_id, 0x04, 0x02, 0x24, 0x01])

    # Calculate the checksum
    checksum = (~(servo_id + 0x04 + 0x02 + 0x24) & 0xFF)

    # Add the checksum to the packet
    packet.append(checksum)

    # Send the instruction packet
    ser.write(packet)

    # Wait for the response packet
    time.sleep(0.1)

    # Read the response packet
    response = ser.read(7)

    # Close the serial port
    ser.close()

    # Check if the response packet is valid
    if len(response) == 7 and response[0] == 0xFF and response[1] == 0xFF and response[2] == servo_id:
        # Extract the present position from the response packet
        present_position = response[5] + (response[6] << 8)
        print(f"Servo ID {servo_id} present position: {present_position} degrees")
    else:
        print(f"Failed to read present position for Servo ID {servo_id}")

# Example usage
read_servo_position(0x03)  # Replace with the appropriate servo ID
