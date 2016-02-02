#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import socket
import getpass
import threading

from socket import AF_INET, SOCK_STREAM

SSH_PORT = 4242
LOCALHOST_ADDR = '127.0.0.1'

NO_ACCES_STR = "Your login informations granted to you no acces !"

class SSHClient(object):
	def __init__(self, hostname=LOCALHOST_ADDR, port=SSH_PORT):
		self.port = port
		self.hostname = hostname

		self.addr_infos = socket.getaddrinfo(self.hostname, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM)[0]

		print "[+] Welcome on ssh client"
		self.username = raw_input("[+] Enter your login please (leave blank for {}): ".format(getpass.getuser()))
		if self.username == '':
			self.username = getpass.getuser()
		self.user_passwd = getpass.getpass("[+] Enter your password please : ")
		
		try:
			self.sock = socket.socket(self.addr_infos[0], self.addr_infos[1], self.addr_infos[2])
		except socket.error as error:
			print "[-] Error : Can't create the socket.\n\t--> error : {}".format(error)

		self.listen_user = threading.Thread(None, self._listen_user, None)
		# self.listen_server = threading.Thread(None, self._listen_server, None)

		self.connect()
		self.run()

	def connect(self):
		try:
			self.sock.connect(self.addr_infos[-1])
			print "[+] We are now connect to %s:%s" % (self.hostname, self.port)
		except Exception, e:
			print "[-] Error : Can't connect socket to (%s:%d): %s" % (
				self.hostname, self.port, e)
			sys.exit(1)

	def _listen_user(self):
		sbuffer = 8192
		while 42:
			user_cmd = raw_input("You> ")
			if user_cmd and user_cmd != 'exit':
				self.sock.sendall(user_cmd)
				self.sock.settimeout(5)
				server_response = self.sock.recv(sbuffer)
				if server_response:
					print "server>\n" + server_response
				else:
					continue
			elif user_cmd == 'exit':
				print "[+] Disconnected ! Bye Bye see ya !"
				sys.exit(0)

	# def _listen_server(self):
	# 	listen_socket = socket.socket(AF_INET, SOCK_STREAM)
	# 	listen_socket.bind(('127.0.0.1', 8888))
	# 	listen_socket.listen(42)
	# 	while 42:
	# 		client, addr = listen_socket.accept()
	# 		if client and addr:
	# 			print "[+] New client connected (%s:%s)" % (addr[0], addr[1])

	def run(self):
		sbuffer = 8192
		# print "[+] Run server listening thread"
		# self.listen_server.start()
		print "[+] Run client listening thread"
		self.sock.sendall("logs:%s:%s" % (self.username, self.user_passwd))
		server_response = self.sock.recv(sbuffer)
		print "server> %s" % (server_response)
		if server_response and server_response != NO_ACCES_STR:
			user_choice = raw_input("You> ")
			if user_choice and user_choice != 'exit':
				self.sock.sendall(user_choice)
				server_response = self.sock.recv(sbuffer)
				if server_response:
					print "server> %s" % (server_response)
				else:
					print "[+] Disconnected ! Bye Bye see ya !"
					sys.exit(0)
			else:
				print "[+] Disconnected ! Bye Bye see ya !"
				sys.exit(0)
		else:
			print "[+] Disconnected ! Bye Bye see ya !"
			sys.exit(0)

		self.listen_user.start()

	def __del__(self):
		if self.sock:
			self.sock.close()

if __name__ == '__main__':
	SSHClient()