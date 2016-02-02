#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import libssh2
import paramiko
import threading

from acl import Acl
from spatch_client import SSHSpatchClient
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

SSH_PORT = 22
LOCALHOST_ADDR = '127.0.0.1'

class ConnectedClient(threading.Thread):
	def __init__(self, socket, addr):
		threading.Thread.__init__(self)

		self.acl = Acl()

		self.sock = socket
		self.sock_addr = addr

		self.username = None
		self.user_passwd = None

		self.ssh_client = None

	def _check_logs(self, client_logs):
		sbuffer = 8192
		self.username = client_logs.split(':')[1]
		self.user_passwd = client_logs.split(':')[2]

		if self.acl.check_user(self.username, self.user_passwd):
			allowed_servers = self.acl.get_user_allowed_servers(self.username)

			response = "Welcome on spatch proxy !"
			response += "You have granted access to those servers on our network, make a choice :"

			for i in range(len(allowed_servers)):
				response += "\n\t%s) %s" % (i, allowed_servers[i]["name"])
			self.sock.sendall(response)
			
			client_choice = self.sock.recv(sbuffer)

			if int(client_choice) >= 0 and int(client_choice) <= len(allowed_servers)-1:
				for server in self.acl.servers:
					if server["name"] == allowed_servers[int(client_choice)]["name"]:
						self.ssh_client = SSHSpatchClient(server["username"],
														  server["password"],
														  hostname=allowed_servers[int(client_choice)]["address"],
														  port=int(allowed_servers[int(client_choice)]["port"]))
				self.sock.sendall("Your are now connected to %s" % (allowed_servers[int(client_choice)]["name"]))
		else:
			response = "Your login informations granted to you no acces !"
			self.sock.sendall(response)
			self.sock.close()

	def run(self):
		sbuffer = 8192
		print "[+] New client %s:%s" % (self.sock_addr[0], self.sock_addr[1])
		while 42:
			client_cmd = str(self.sock.recv(sbuffer))
			if client_cmd:
				if 'logs:' in client_cmd:
					self._check_logs(client_cmd)
				else:
					print "Received from %s:%s> %s" % (self.sock_addr[0], self.sock_addr[1], client_cmd)
					self.sock.sendall(self.ssh_client.execute(client_cmd))

class SSHSpatchServer(object):
	def __init__(self, hostname=LOCALHOST_ADDR, port=SSH_PORT):
		self.port = port
		self.hostname = LOCALHOST_ADDR

		self.channel = None
		self.session = libssh2.Session()

		self.connected_clients = []

		try:
			self.sock = socket.socket(AF_INET, SOCK_STREAM)
		except socket.error as error:
			print "[-] Error: Can't create socket.\n\t--> with message: %s" % (
					error)
			sys.exit(1)

		self._prepare_sock()
		self.listen()
		self.waiting_connection()

	def start_client(self, client_sock):
		SSHSpatchClient('user', 'passwd', sock=client_sock)

	def startup(self, client_sock, client_addr):
		# try:
		_buffer = 8192000
		_socket = socket.socket(AF_INET, SOCK_STREAM)
		_socket.connect(('127.0.0.1', 22))
		self.session.set_banner()
		self.session.startup(_socket)
		self.session.userauth_password('xod', 'xgxzpqkux953369=a')
		chan = self.session.open_session()
		self.session.direct_tcpip('127.0.0.1', 8888, '127.0.0.1', 22)
		read_channel = chan.execute('ls -la')

		while True:
			data = chan.read(_buffer)
			if data == '' or data == None: print "Commande inconnue"
			print data.strip()

		# except Exception, e:
		# 	print "[-] Error: %s" % e
		# 	sys.exit(1)

	def _prepare_sock(self):
		try:
			self.sock.bind((self.hostname, self.port))
		except socket.error as error:
			print "[-] Error: Failed to bind on %s:%s\n\t--> with message: %s" % (
					self.hostname, str(self.port), error)
			sys.exit(1)

	def listen(self):
		try:
			self.sock.listen(42)
		except socket.error as error:
			print "[-] Error: Failed to listening on socket.\n\t--> with message: %s" % (
					error)

	def waiting_connection(self):
		print "[+] Listening for connection on port %s" % str(self.port)
		while 42:
			client_sock, sock_addr = self.sock.accept()
			if client_sock and sock_addr:
				client = ConnectedClient(client_sock, sock_addr)
				client.start()
				self.connected_clients.append(client)

			# self.start_client(client)

			# print "[+] New client (%s:%s)" % (sock_addr[0], sock_addr[1])
			# if client_sock and sock_addr:
			# 	self.startup(client_sock, sock_addr)

	def __del__(self):
		self.sock.close()

if __name__ == '__main__':
	server = SSHSpatchServer(port=4242)