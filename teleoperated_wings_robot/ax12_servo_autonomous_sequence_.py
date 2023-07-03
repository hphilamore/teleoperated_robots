import serial
import RPi.GPIO as GPIO
import time

# Serial port settings
SERIAL_PORT = "/dev/serial0"  # Replace with the appropriate port name
BAUDRATE = 1000000  # Baudrate used in the tutorial (57600 bps)

# GPIO pin configuration
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# GPIO.setup(18, GPIO.OUT)  # Control Data Direction Pin

# Enable pin configuration for 74LS241
enable_pin = 18
GPIO.setup(enable_pin, GPIO.OUT)

# Function to enable/disable communication with the servos
def enable_servos(enable):
    GPIO.output(enable_pin, enable)

# Function to control servo position
def set_servo_position(servo_id, position):
    # Open the serial port
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=0.1)

    # Construct the instruction packet
    packet = bytearray([0xFF, 0xFF, servo_id, 0x05, 0x03, 0x1E, 0x00, 0x00])
    packet[7] = position & 0xFF  # Low byte of position
    packet[8] = (position >> 8) & 0xFF  # High byte of position

    # Calculate checksum
    checksum = ~(servo_id + 0x05 + 0x03 + 0x1E + packet[7] + packet[8]) & 0xFF
    packet.append(checksum)

    # Enable communication with the servos
    enable_servos(True)

    # Send the instruction packet
    ser.write(packet)

    # Close the serial port
    ser.close()

    # Disable communication with the servos
    enable_servos(False)

# Sweep the servo positions from 0 to 300 degrees
for position in range(0, 301, 10):
    set_servo_position(1, position)  # Servo ID 1
    set_servo_position(2, position)  # Servo ID 2
    time.sleep(0.1)  # Delay between positions

# Cleanup GPIO
GPIO.cleanup()
