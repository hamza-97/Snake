import socket
from _thread import *
import threading
import curses
import random
import time
import pickle
import sys
from random import randint

clients_arr = []
info_arr = []
# print_lock = threading.Lock() 

def threader(connection,info,num_of_ply,f_xy):
	connection.send((str(num_of_ply)).encode('utf-8'))
	connection.send(pickle.dumps(f_xy))
	
	while True:
		olddata = connection.recv(64)
	
		if olddata:
			data = pickle.loads(olddata)
			print( "first receive ",data)
			if data[0]==1 and data[1] == 1:
				clients_arr.remove(connection)
			elif data[1]==-1:
				tosend = []
				x = randint(2,32)
				y = randint(2,17)
				tosend.append(-1)
				tosend.append(x)
				tosend.append(y)
				olddata = pickle.dumps(tosend)
	
				for c in clients_arr:
					c.send(olddata)
			else:
				for c in clients_arr:
					c.send(olddata)

	
	connection.close()

def main(argv):
	
	num_of_ply = int(argv[3])
	counter = 0
	food_xy = []
	food_x = randint(2,32)
	food_y = randint(2,17)
	food_xy.append(food_x)
	food_xy.append(food_y)
	
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	s.bind((argv[1],int(argv[2])))
	print ("socket binded to post", 8080)
	s.listen(5)
	print ("socket is listening")

	while True:
		client,info = s.accept()
		counter = counter + 1
		msg = str(counter)
		client.send(msg.encode('utf-8'))

		print ("Newly connected client is ", info)
		clients_arr.append(client)
		info_arr.append(info)

		if(counter == num_of_ply):
			for i in range(num_of_ply): 
				start_new_thread(threader,(clients_arr[i],info_arr[i],num_of_ply,food_xy))
	s.close()

if __name__ == '__main__':
	main(sys.argv)