import RPi.GPIO as GPIO
import serial
import os
from time import sleep
from time import time


# Hex values to appear in instruction packet sent to servo
ax_start = 0xFF       # 2 x FF bytes indicate start of incoming packet 
ax_id = 0x01          # servo ID 
ax_goal_length = 0x05 # length of instruction packet (N parameters + 2)
ax_goal_speed_length = 0x07 # length of instruction packet (N parameters + 2)

# instructions for servo to perform 
ax_ping = 0x01
ax_read_data = 0x02
ax_write_data = 0x03
ax_reg_write = 0x04
ax_action = 0x05
ax_reset = 0x06
ax_sync_write = 0x83
ax_ccw_angle_limit_l = 0x08
ax_ccw_al_lt = 0x00
ax_ccw_al_l = 0xFF
ax_ccw_al_h = 0x03
ax_speed_length = 0x05
ax_goal_speed_l = 0x20
ccw = 0
cw = 1


def move(servo_id, position, serial_object):
    """
    Moves a servo with specified ID to specified position (angle in degrees)

    servo_id: servo serial ID number
    position: allowable range (0, 1023), representing angle in degrees range (0, 300)

    """
    
    P = position  # position as integer representation of 10-bit value (in range 0 to 1024)

    # print(type(P))

    # print(P/1024 * 300) # Show angle in degrees

    h = P >> 8    # value of high 8 bit byte

    l = P & 0xff  # value of low 8-bit byte

    checksum = ~(servo_id + ax_goal_length + ax_write_data + 0x1E + h + l) & 0xff

    checksum = format(checksum, '#04x') # convert to hex number full representation (with 0x...)



    instruction_packet = (format(ax_start, '02x') + " " +
                          format(ax_start, '02x') + " " +
                          format(servo_id, '02x') + " " + 
                          format(ax_goal_length, '02x') + " " +
                          format(ax_write_data, '02x') + " " +
                          format(0x1E, '02x') + " " +
                          format(l, '02x') + " " +
                          format(h, '02x') + " " +
                          checksum[2:] 
                          ).upper()
                          #str(ax_write_data) + str(0x1E) + str(l) + str(h) + str(checksum))
    print(instruction_packet)
    serial_object.write(bytearray.fromhex(instruction_packet))

    return(instruction_packet)


def move_speed(servo_id, position, speed, serial_object):
    """
    Moves a servo with specified ID to specified position (angle in degrees) and specified speed

    servo_id: servo serial ID number
    position: allowable range (0, 1023), representing angle in degrees range (0, 300)
    speed: speed of rotation, allowable range (0, 1023)

    """
    # P = int(angle/300 * 1024)
    P = position  # position as integer representation of 10-bit value (in range 0 to 1024)

    # print(type(P))

    # print(P/1024 * 300) # Show angle in degrees

    h = P >> 8    # value of high 8 bit byte

    l = P & 0xff  # value of low 8-bit byte

    S = speed

    sh = S >> 8    # value of high 8 bit byte

    sl = S & 0xff  # value of low 8-bit byte



    checksum = ~(servo_id + ax_goal_speed_length + ax_write_data + 0x1E + h + l + sh + sl) & 0xff

    checksum = format(checksum, '#04x') # convert to hex number full representation (with 0x...)



    instruction_packet = (format(ax_start, '02x') + " " +
                          format(ax_start, '02x') + " " +
                          format(servo_id, '02x') + " " + 
                          format(ax_goal_speed_length, '02x') + " " +
                          format(ax_write_data, '02x') + " " +
                          format(0x1E, '02x') + " " +
                          format(l, '02x') + " " +
                          format(h, '02x') + " " +
                          format(sl, '02x') + " " +
                          format(sh, '02x') + " " +
                          checksum[2:] 
                          ).upper()
                          #str(ax_write_data) + str(0x1E) + str(l) + str(h) + str(checksum))

    print(instruction_packet)

    serial_object.write(bytearray.fromhex(instruction_packet))

    return(instruction_packet)


def set_endless(servo_id, status, serial_object):

    """
    Set a servo with specified ID to continous rotation/servo mode

    servo_id: servo serial ID number
    status: True= continuous rotation mode, False = servo mode
    """
    
    if status: # turn endless rotation on               
    
        checksum = ~(servo_id + ax_goal_length + ax_write_data + ax_ccw_angle_limit_l) & 0xff
        checksum = format(checksum, '#04x') # convert to hex number full representation (with 0x...) 
        
        #print('checksum = ', checksum)
        
        instruction_packet = (format(ax_start, '02x') + " " +
                              format(ax_start, '02x') + " " +
                              format(servo_id, '02x') + " " + 
                              format(ax_goal_length, '02x') + " " +
                              format(ax_write_data, '02x') + " " +
                              format(ax_ccw_angle_limit_l, '02x') + " " +
                              format(ax_ccw_al_lt, '02x') + " " +
                              format(ax_ccw_al_lt, '02x') + " " +
                              checksum[2:] 
                               ).upper()
                              
    
    else: # turn endless rotation off
        
        checksum = ~(servo_id + ax_goal_length + ax_write_data +
                     ax_ccw_angle_limit_l + ax_ccw_al_l + ax_ccw_al_h) & 0xff
        checksum = format(checksum, '#04x') # convert to hex number full representation (with 0x...)
        
        # print('checksum = ', checksum)
        
        instruction_packet = (format(ax_start, '02x') + " " +
                              format(ax_start, '02x') + " " +
                              format(servo_id, '02x') + " " + 
                              format(ax_goal_length, '02x') + " " +
                              format(ax_write_data, '02x') + " " +
                              format(ax_ccw_angle_limit_l, '02x') + " " +
                              format(ax_ccw_al_l, '02x') + " " +
                              format(ax_ccw_al_h, '02x') + " " +
                              checksum[2:] 
                              ).upper()
        
    #print(instruction_packet)
    
    serial_object.write(bytearray.fromhex(instruction_packet))
    
    return(instruction_packet)


def turn(servo_id, direction, speed, serial_object):

    """
    Sets speed and direction of motor with specified ID in continous rotation mode 

    servo_id: servo serial ID number
    direction: cw = clockwise rotation, ccw = counter-clockwise rotation
    speed: 
    """

    if direction == ccw:
        #print('ccw')
        speed_h = speed >> 8 # convert position as 10-bit number to high 8 bit byte
        speed_l = speed & 0xff
        
    else:
        #print('cw')
        speed_h = (speed >> 8) + 4
        speed_l = speed & 0xff
        
    checksum = ~(servo_id + ax_speed_length + ax_write_data +
                 ax_goal_speed_l + speed_l + speed_h) & 0xff
    
    checksum = format(checksum, '#04x') # convert to hex number full representation (with 0x...)
    
    #print('checksum = ', checksum)
    
    instruction_packet = (format(ax_start, '02x') + " " +
                          format(ax_start, '02x') + " " +
                          format(servo_id, '02x') + " " + 
                          format(ax_speed_length, '02x') + " " +
                          format(ax_write_data, '02x') + " " +
                          format(ax_goal_speed_l, '02x') + " " +
                          format(speed_l, '02x') + " " +
                          format(speed_h, '02x') + " " +
                          checksum[2:] 
                          ).upper()
        
    #print(instruction_packet)
    
    serial_object.write(bytearray.fromhex(instruction_packet))
    
    return(instruction_packet)


# def sweep(servo_id, positions, wait, serial_object):

#     """
#     Sweep a servo with specified ID over angular range specified
#     """
#     for p in positions:
#         move(servo_id, p, serial_object)
#         sleep(wait)
#         # move_speed(servo_id, p, speed, serial_object)
#         print(p)
        


# def forwards(serial_object, left=0x02, right=0x01):
#     """
#     Turn two servos labelled as left and right in same direction if configured as 
#     differential drive wheels on a robot
#     """
#     GPIO.output(18,GPIO.HIGH) 
#     set_endless(left, True, serial_object)
#     set_endless(right, True, serial_object)
    
#     turn(left, ccw,1000, serial_object)
#     turn(right, cw, 1000, serial_object)    


def move_check(servo_id, position):

    """
    A visual check that the high and low 8 bit byte are correct 
    """

    P = position            # position as 10-bit number 

    B = P/256               # seperate into 2 8 bit bytes by dividing by max value of 8 bit byte 

    H = int(B // 1)         # decimal value of high byte, convert to intager

    L = B - H                     
    L = int(L * 256)        # decimal value of low byte

    H = hex(H)

    L = hex(L)

    print(H,L)



if __name__ == "__main__":

    # Setup GPIO pins 
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    enable_pin = 18.                  # Data Direction Pin
    GPIO.setup(enable_pin,GPIO.OUT)     

    # Create serial object 
    Dynamixel=serial.Serial("/dev/serial0",baudrate=1000000,timeout=0.1, bytesize=8)   

    # Set motors with ID 1-2 to servo mode
    set_endless(0x01, False, Dynamixel)
    set_endless(0x02, False, Dynamixel)

    # Set motors with ID 3-4 to continuous rotation mode
    set_endless(0x03, True, Dynamixel)
    set_endless(0x04, True, Dynamixel)

    # Enable send data to motors
    GPIO.output(18,GPIO.HIGH)

    while True:
        # Move motors 1-2 to central position
        move(0x01, 512, Dynamixel)
        move(0x02, 512, Dynamixel)

        # Sweep motor ID 1 through range of angles
        for i in range(513, 1024):
            move(0x01, i, Dynamixel)
            sleep(0.005)

        # Move motor ID 2 to a position with a specified speed
        move_speed(0x02, 150, 500, Dynamixel)

        # Rotate motor ID 3 continuousy in clockwise direction at full speed
        turn(0x03, 'cw', 1023, Dynamixel)

        # Rotate motor ID 4 continuousy in counter-clockwise direction at half speed
        turn(0x04, 'ccw', 512, Dynamixel)

        # Wait for 5 seconds
        sleep(5)

        # Stop motors ID 3-4
        turn(0x03, 'cw', 0, Dynamixel)
        turn(0x04, 'ccw', 0, Dynamixel)


