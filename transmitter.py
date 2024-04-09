
import socket

class Transmitter():

	def __init__(self, 
				 HOST = "192.168.138.7", 
				 PORT = 65448
				 ):

		self.HOST = HOST 
		self.PORT = PORT

	def send_command_to_server(self):
		"""
		Uses sockets to send command to server robot over local network
		"""
		# Send command to server socket on raspberry pi
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((self.HOST, self.PORT))
			s.sendall(self.command.encode())



