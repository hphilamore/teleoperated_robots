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

# Create serial object 
Dynamixel=serial.Serial("/dev/serial0",
                        baudrate=1000000,
                        timeout=0.1, 
                        bytesize=8)   # UART in ttyS0 @ 1Mbps

Dynamixel.write(bytearray.fromhex("FF FF 01 04 02 36 02 D2"))   # Read Position of Servo with ID = 1
GPIO.output(18,GPIO.LOW)
startDynamixel = Dynamixel.read()
startDynamixel = Dynamixel.read()
print(startDynamixel)
idDynamixel = Dynamixel.read()
print(idDynamixel )
lenghtDynamixel = Dynamixel.read()
errorDynamixel = Dynamixel.read()
posDynamixel = Dynamixel.read(2)
chkDynamixel = Dynamixel.read()
print("Servo Position = " , int.from_bytes(posDynamixel,byteorder='little'))
time.sleep(1)

Dynamixel.write(bytearray.fromhex("FF FF 02 04 02 24 02 D2"))   # Read Position of Servo with ID = 1
GPIO.output(18,GPIO.LOW)
time.sleep(0.1)
startDynamixel = Dynamixel.read(7)
present_position = startDynamixel[5] + (startDynamixel[6] << 8)
print(f"Servo ID {servo_id} present position: {present_position} degrees")
# startDynamixel = Dynamixel.read()
# idDynamixel = Dynamixel.read()
# lenghtDynamixel = Dynamixel.read()
# errorDynamixel = Dynamixel.read()
# posDynamixel = Dynamixel.read(2)
# chkDynamixel = Dynamixel.read()
# print("Servo Position = " , int.from_bytes(posDynamixel,byteorder='little'))
# time.sleep(1)

Dynamixel.write(bytearray.fromhex("FF FF 03 04 02 24 02 D2"))   # Read Position of Servo with ID = 1
GPIO.output(18,GPIO.LOW)
startDynamixel = Dynamixel.read()
startDynamixel = Dynamixel.read()
idDynamixel = Dynamixel.read()
lenghtDynamixel = Dynamixel.read()
errorDynamixel = Dynamixel.read()
posDynamixel = Dynamixel.read(2)
chkDynamixel = Dynamixel.read()
print("Servo Position = " , int.from_bytes(posDynamixel,byteorder='little'))
time.sleep(1)

Dynamixel.write(bytearray.fromhex("FF FF 04 04 02 24 02 D2"))   # Read Position of Servo with ID = 1
GPIO.output(18,GPIO.LOW)
startDynamixel = Dynamixel.read()
startDynamixel = Dynamixel.read()
idDynamixel = Dynamixel.read()
lenghtDynamixel = Dynamixel.read()
errorDynamixel = Dynamixel.read()
posDynamixel = Dynamixel.read(2)
chkDynamixel = Dynamixel.read()
print("Servo Position = " , int.from_bytes(posDynamixel,byteorder='little'))
time.sleep(1)

# def read_servo_position(servo_id):
#     # Open the serial port
#     ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE)

#     # Construct the instruction packet
#     packet = bytearray([0xFF, 0xFF, servo_id, 0x04, 0x02, 0x24, 0x01])

#     # Calculate the checksum
#     checksum = (~(servo_id + 0x04 + 0x02 + 0x24) & 0xFF)

#     # Add the checksum to the packet
#     packet.append(checksum)

#     # Send the instruction packet
#     ser.write(packet)

#     # Wait for the response packet
#     time.sleep(0.1)

#     # Read the response packet
#     response = ser.read(7)

#     # Close the serial port
#     ser.close()

#     # Check if the response packet is valid
#     if len(response) == 7 and response[0] == 0xFF and response[1] == 0xFF and response[2] == servo_id:
#         # Extract the present position from the response packet
#         present_position = response[5] + (response[6] << 8)
#         print(f"Servo ID {servo_id} present position: {present_position} degrees")
#     else:
#         print(f"Failed to read present position for Servo ID {servo_id}")

# # Example usage
# read_servo_position(0x03)  # Replace with the appropriate servo ID
