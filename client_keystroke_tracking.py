
import curses
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

class KeystrokeTracker(Transmitter):

	def __init__(self, 
		         send_command,
		         HOST = "192.168.138.7",
		         PORT = 65448
		         ):

		super().__init__(HOST, PORT)

		self.send_command = send_command
		self.command = ''


	def track_keys(self):

	    """
	    Tracks keystrokes typed in terminal and converts to commands
	    """

	    # Set up terminal to track keys
	    screen = curses.initscr()
	    curses.noecho() 
	    curses.cbreak()
	    screen.keypad(True)


	    # Default command to send 
	    self.command = 'stop'

	    try:

	        while(True):

	            # Get last typed character
	            char = screen.getch()


	            if char == ord('q'):
	                print("quit")
	                break

	            elif char == curses.KEY_UP:
	                print("up")
	                self.command = 'forward'

	            elif char == curses.KEY_DOWN:
	                print("down")
	                self.command = 'backward'

	            elif char == curses.KEY_RIGHT:
	                print("right")
	                self.command = 'right'

	            elif char == curses.KEY_LEFT:
	                print("left")
	                self.command = 'left'

	            elif char == ord('s'): #10:
	                print("stop")
	                self.command = 'stop' 

	            # Send command to server socket on raspberry pi
	            if self.send_command:
	            	self.send_command_to_server()

	            # send_command_to_server(HOST, PORT, command)
	            # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	            #     s.connect((HOST, PORT))
	            #     s.sendall(command.encode())

	    except KeyboardInterrupt:
	        #Close down curses properly, inc turn echo back on!
	        curses.nocbreak(); screen.keypad(0); curses.echo()
	        curses.endwin()
	        sys.exit(1)

if __name__ == '__main__':
	keystroke_tracker = KeystrokeTracker(send_command, HOST, PORT)
	keystroke_tracker.track_keys()
