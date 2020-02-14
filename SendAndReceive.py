import socket
import signal

class machineDetails():
	def __init__(self, machine_name="", machine_ip=""):
		self.populate_details()

	def populate_details():
		with open("configuration") as conf_file:
			# Get Machine name
			self.machine_name = fp.readline()

			# Get Mahine IP
			self.machine_ip = fp.readline()

			# Get neigbhor details
			neigbhor_details = fp.readline()

		# TODO confirm input are correct from file.
		self.populate_neigbhor(neigbhor_details)

	def populate_neigbhor(self, neigbhor_details):
		neigbhor_ip_port_list = neigbhor_details.split(',')
		for ip_port in neigbhor_ip_port_list:
			neigbhor_ip_port = ip_port.split(':')
			self.list_neigbhors.append(neigbhor_ip_port)


class socketConnection():
	def __init__(self, port=80):
		self.socket_conn = socket.socket()
		self.port = port
		self.list_neigbhors_

	def bind_connection(self, host_name=''):
		self.socket_conn.bind(host_name, self.port)

	def set_max_connections(self, max_connections):
		self.max_connections = max_connections
		self.socket_conn.listen(self.max_connections)

	def get_connection_obj(self):
		return self.socket_conn

	def start_listening(self):
		while True:
			neigbhor_conn, address = self.socket_conn.accept()
			self.current_neigbhor_conn = neigbhor_conn

			# Receive data from neigbhor and check if you get any
			# updated data. If there is any update send it to
			# other neigbhors.
			# neigbhor_conn.recv(4096)

			print("Got connection request from {0}".format(address))
			self.update_neigbhor()

			# TODO: Add 

	def update_neigbhor(self):
		self.current_neigbhor_conn.send("I have an update...")
		self.current_neigbhor_conn.close()

	def close_connections(self):
		self.current_neigbhor_conn.close()
		self.socket_conn.close()



if __name__ == '__main__':

	socket_conn = socketConnection()

	signal.signal(signal.SIGINT, socket_conn.close_connections)

	socket_conn.bind_connection()
	socket_conn.set_max_connections()
	socket_conn.start_listening()

