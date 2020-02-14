import socket
import signal
from threading import Thread
import time

DEFAULT_PORT=12345

class networkNodesInfo():
	def __init__(self, machine_name="", machine_ip=""):
		# Dict of neighbor host ip key:value pair.
		self.network_map = {}

		# List of neighbor IPs
		self.list_neighbors = []

		self.populate_details()

		# Dict to maintain IP to hostname mapping.
		self.ip_host_map = {self.machine_ip:self.machine_name}

	def populate_details(self):
		with open("configuration") as conf_file:
			# Get Machine name
			self.machine_name = conf_file.readline().split('\n')[0]

			# Get Machine IP
			self.machine_ip = conf_file.readline().split('\n')[0]

			# Get neighbor details
			neighbor_details = conf_file.readline().split('\n')[0]

		# TODO confirm input are correct from file.
		self.populate_neighbor(neighbor_details)

	def populate_neighbor(self, neighbor_details):
		neighbor_ip_port_list = neighbor_details.split(',')
		for ip_port in neighbor_ip_port_list:
			neighbor_ip = ip_port.split(':')[0].strip()

			try:
				neighbor_port = ip_port.split(':')[1].strip()
			except Exception as e:
				neighbor_port = DEFAULT_PORT
				print("Ignore Exception {0}".format(e))

			self.list_neighbors.append([neighbor_ip, neighbor_port])

			if self.machine_ip not in self.network_map:
				self.network_map[self.machine_ip] = [neighbor_ip]
			else:
				self.network_map[self.machine_ip].append(neighbor_ip)

	def get_neighbor_list(self):
		return self.list_neighbors

	def get_network_map(self):
		return self.network_map

	def get_ip_host_map(self):
		return self.ip_host_map

	def add_ip_host(self, ip, hostname):
		if ip not in self.ip_host_map:
			self.ip_host_map[ip] = hostname

	def update_network_node(self, node_ip, neighbor_list):
		if node_ip not in self.network_map:
			self.network_map[node_ip] = neighbor_list

	def get_data_for_update(self):
		all_node_udpate = [self.ip_host_map, self.network_map]
		return all_node_udpate

	def print_network_node_mapping(self):
		for localhost_ip, neighbor_ip_list in self.network_map.items():
			name_list = []
			for ip in neighbor_ip_list:
				name_list.append(self.ip_host_map[ip])

			print("{0} : {1}".format(
				  self.ip_host_map[localhost_ip], str(name_list)))


class clientConnection():
	def __init__(self, networkNodesInfo_obj, host_ip, port):
		timeout = 50
		connection_established = False
		while timeout:
			try:
				self.socket_conn = socket.socket()
				self.socket_conn.connect((host_ip, int(port)))

				connection_established = True
				timeout = 0
			except socket.error as e:
				if e.errno == 61:
					print("Seems server is not up, waiting for 5 secs...")
					time.sleep(5)
					self.socket_conn.close()
					timeout -=5
				else:
					print("Socket error: {}".format(e))
					timeout = 0

			except Exception as e:
				print("Generic exception occurred: {}".format(e))
				timeout = 0

		try:
			if connection_established:
				self.send_update(networkNodesInfo_obj)
		except Exception as e:
			print("Exception {} while sending data to {}.".format(host_ip, e))

	def send_update(self, networkNodesInfo_obj):
		self.socket_conn.send(str(networkNodesInfo_obj.get_data_for_update()))
			



class serverConnection():
	def __init__(self, networkNodesInfo_obj, port=DEFAULT_PORT):
		self.socket_conn = socket.socket()
		self.port = port
		self.networkNodesInfo_obj = networkNodesInfo_obj
		self.networkNodesInfo_obj.print_network_node_mapping()

	def bind_connection(self, host_name=''):
		self.socket_conn.bind((host_name, self.port))

	def set_max_connections(self, max_connections):
		self.max_connections = max_connections
		self.socket_conn.listen(self.max_connections)

	def get_connection_obj(self):
		return self.socket_conn

	def start_listening(self):
		while True:
			neighbor_conn, address = self.socket_conn.accept()
			self.current_neighbor_conn = neighbor_conn

			# Receive data from neighbor and check if you get any
			# updated data. If there is any update send it to
			# other neighbors.
			incoming_data = self.socket_conn.recv(4096)

			print("Got connection request from {0}".format(address))
			print("Got data as: {0}".format(incoming_data))
			self.current_neighbor_conn.close()

			self.update_neighbor()


	def update_neighbor(self):
		neighbors_list = self.networkNodesInfo_obj.get_neighbor_list()
		for neighbor in neighbors_list:
			clientConnection(self.networkNodesInfo_obj, neighbor[0], neighbor[1])

	def close_connections(self):
		self.current_neighbor_conn.close()
		self.socket_conn.close()



if __name__ == '__main__':

	networkNodesInfo_obj = networkNodesInfo()

	neighbors_list = networkNodesInfo_obj.get_neighbor_list()
	for neighbor in neighbors_list:
		update_neighbor_thread = Thread(target = clientConnection,
			   args=(networkNodesInfo_obj, neighbor[0], neighbor[1])) 
		update_neighbor_thread.start()

	socket_conn = serverConnection(networkNodesInfo_obj)
	socket_conn.bind_connection()
	socket_conn.set_max_connections(100)
	socket_conn.start_listening()

	signal.signal(signal.SIGINT, socket_conn.close_connections)

