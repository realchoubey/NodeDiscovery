from os import listdir
from os.path import isfile, join


import subprocess
import sys
import time


def close_connections(processes):
	print("Killing all")
	for proc in processes:
		proc.kill()

if __name__ == '__main__':
	
	curr_dir = "."
	processes_list = []

	all_files = [f for f in listdir(curr_dir) if isfile(join(curr_dir, f))]

	for file in all_files:
		if file.startswith("config"):
			proc = subprocess.Popen(["python", "SendAndReceive.py", "-c", file])
			processes_list.append(proc)

	time.sleep(20)
	close_connections(processes_list)



