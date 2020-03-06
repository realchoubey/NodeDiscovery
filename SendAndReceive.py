#!/usr/bin/python

from threading import Thread

import collections
import getopt
import os
import pickle
import socket
import sys
import time

default_port=12345

class networkNodesInfo():
	def __init__(self, start_time, configuration_file="configuration"):
		self.all_node_discovered = False
		self.start_time = start_time
		self.extra_time = 0

		# Dict of neighbor host ip key:value pair.
		self.network_map = {}

		# List of neighbor IPs
		self.list_neighbors = []

		self.populate_details(configuration_file)

		# Dict to maintain IP to hostname mapping.
		self.ip_host_map = {self.machine_ip:self.machine_name}

	def get_machine_port(self):
		return self.port

	def get_host_ip(self):
		return self.machine_ip.split(':')[0]

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
		return pickle.dumps(all_node_udpate)

	def populate_details(self, configuration_file):
		try:
			with open(configuration_file) as conf_file:
				# Get Machine name
				self.machine_name = conf_file.readline().split('\n')[0]

				# Get Machine IP and port number
				machine_ip_info = conf_file.readline().split('\n')[0]
				self.machine_ip = machine_ip_info
				self.port = int(machine_ip_info.split(':')[1])
				if not self.port:
					self.port = default_port

				# Get neighbor details
				neighbor_details = conf_file.readline().split('\n')[0]

			# TODO confirm input are correct from file.
			self.populate_neighbor(neighbor_details)
		except Exception as e:
			print("Exception {} occurred".format(e))
			raise e

	def populate_neighbor(self, neighbor_details):
		neighbor_ip_port_list = neighbor_details.split(',')
		for ip_port in neighbor_ip_port_list:
			# As of now keep port with IP
			# neighbor_ip = ip_port.split(':')[0].strip()
			neighbor_ip = ip_port.strip()

			# Get port number.
			try:
				neighbor_port = int(ip_port.split(':')[1].strip())
			except Exception as e:
				neighbor_port = default_port
				print("Ignore Exception {0}".format(e))

			self.list_neighbors.append([neighbor_ip, neighbor_port])

			if self.machine_ip not in self.network_map:
				self.network_map[self.machine_ip] = [neighbor_ip]
			else:
				if neighbor_ip not in self.network_map[self.machine_ip]:
					self.network_map[self.machine_ip].append(neighbor_ip)

	def print_network_node_mapping(self):
		name_list_all = []
		all_discovered = True
		for localhost_ip, neighbor_ip_list in sorted(self.network_map.items()):
			name_list = []
			for ip in neighbor_ip_list:
				if ip in self.ip_host_map:
					name_list.append(self.ip_host_map[ip])
				else:
					all_discovered = False
					name_list.append(ip)

			name_list_all.append(name_list)

		self.all_node_discovered = all_discovered

		if self.all_node_discovered:
			idx = 0
			for localhost_ip, neighbor_ip_list in sorted(self.network_map.items()):
				print("{0} : {1}".format(
					  self.ip_host_map[localhost_ip], sorted(name_list_all[idx])))
				idx += 1

			time_taken_for_discovery = round(time.time() - self.start_time, 2)
			print("Total time take for discovery from machine {}: {} seconds"
				  .format(self.machine_name, time_taken_for_discovery - self.extra_time))

	def update_all_machine_details(self, incoming_data):
		current_time = time.time()

		if not self.all_node_discovered:
			ip_host_map = incoming_data[0]
			updated_network_map = incoming_data[1]

			# Update name of machine.
			for ip, name in ip_host_map.items():
				if ip not in self.ip_host_map:
					self.ip_host_map[ip] = name

			# Update network node info.
			for localhost_ip, neighbor_ip_list in updated_network_map.items():
				if localhost_ip in self.network_map:
					for neighbor in neighbor_ip_list:
						if neighbor not in self.network_map[localhost_ip]:
							self.network_map[localhost_ip].append(neighbor)
				else:
					self.network_map[localhost_ip] = neighbor_ip_list

			self.print_network_node_mapping()

		self.extra_time += round(time.time() - current_time, 2)


	def compare_incoming_current_data(self, incoming_data):
		current_time = time.time()

		ip_host_map = incoming_data[0]
		updated_network_map = incoming_data[1]

		if collections.Counter(updated_network_map) == collections.Counter(self.network_map) \
		  and collections.Counter(ip_host_map) == collections.Counter(self.ip_host_map):
		  	self.extra_time += round(time.time() - current_time, 2)
			return False

		self.extra_time += round(time.time() - current_time, 2)
		return True


class clientConnection():
	def __init__(self, networkNodesInfo_obj, host_ip, port):
		timeout = 300
		connection_established = False
		while timeout:
			try:
				self.socket_conn = socket.socket()
				self.socket_conn.connect((host_ip, port))

				connection_established = True
				timeout = 0
			except socket.error as e:
				if e.errno == 61:
					# print("Seems server is not up, waiting for 5 secs...")
					# time.sleep(5)
					self.socket_conn.close()
					timeout -=5
				else:
					# print("Socket error at : {}".format(e))
					timeout = 0

			except Exception as e:
				# print("Generic exception occurred: {}".format(e))
				timeout = 0

		try:
			if connection_established:
				self.send_update(networkNodesInfo_obj)
		except Exception as e:
			print("Exception {} while sending data to {}.".format(host_ip, e))

	def send_update(self, networkNodesInfo_obj):
		data_stream = networkNodesInfo_obj.get_data_for_update()
		self.socket_conn.send(data_stream)


class serverConnection():
	def __init__(self, networkNodesInfo_obj, port=default_port):
		self.socket_conn = socket.socket()
		self.host_ip = networkNodesInfo_obj.get_host_ip()
		self.port = port
		self.networkNodesInfo_obj = networkNodesInfo_obj

	def bind_connection(self, host_ip=''):
		self.socket_conn.bind((host_ip, self.port))

	def set_max_connections(self, max_connections):
		self.max_connections = max_connections
		self.socket_conn.listen(self.max_connections)

	def get_connection_obj(self):
		return self.socket_conn

	def start_server(self):
		self.bind_connection(self.host_ip)
		self.set_max_connections(100)
		self.start_listening()

	def start_listening(self):
		while True:
			neighbor_conn, address = self.socket_conn.accept()
			self.current_neighbor_conn = neighbor_conn

			# Receive data from neighbor and check if you get any
			# updated data. If there is any update send it to
			# other neighbors.
			# TODO Read in stream so that we can have more data reads.
			incoming_data = self.current_neighbor_conn.recv(5120)
			data_object = pickle.loads(incoming_data)

			if networkNodesInfo_obj.compare_incoming_current_data(data_object):
				# Update this machine node information.
				networkNodesInfo_obj.update_all_machine_details(data_object)
				self.current_neighbor_conn.send(networkNodesInfo_obj.get_data_for_update())

				# Update and close.
				self.update_neighbor()

			# self.current_neighbor_conn.close()

	def update_neighbor(self):
		neighbors_list = self.networkNodesInfo_obj.get_neighbor_list()
		for neighbor in neighbors_list:
			host_ip = neighbor[0].split(':')[0]
			port_number = neighbor[1]
			clientConnection(self.networkNodesInfo_obj, host_ip, port_number)

	def close_connections(self):
		self.current_neighbor_conn.close()
		self.socket_conn.close()


if __name__ == '__main__':

	start_time = time.time()
	config_file = "configuration"

	try:
		opts, args = getopt.getopt(sys.argv[1:],"c:p",["config=","port="])
	except getopt.GetoptError:
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-c", "--config"):
			config_file = arg
		elif opt in ("-p", "--port"):
			default_port = arg

	try:
		networkNodesInfo_obj = networkNodesInfo(start_time, config_file)
	except Exception as e:
		sys.exit(0)

	# Start server thread.
	socket_conn = serverConnection(networkNodesInfo_obj,
								   networkNodesInfo_obj.get_machine_port())
	server_thread = Thread(target = socket_conn.start_server) 
	server_thread.start()


	# Update all neighbors with current information.
	neighbors_list = networkNodesInfo_obj.get_neighbor_list()
	for neighbor in neighbors_list:
		host_ip = neighbor[0].split(':')[0]
		port_number = neighbor[1]
		update_neighbor_thread = Thread(target = clientConnection,
			   args=(networkNodesInfo_obj, host_ip, port_number)) 
		update_neighbor_thread.start()

	# TODO Close all the connections gracefully for all threads.

