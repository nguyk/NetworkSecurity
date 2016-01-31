#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import libssh2

from client import SSHClient
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

SSH_PORT = 22
LOCALHOST_ADDR = '127.0.0.1'

class SSHServer(object):
	def __init__(self, hostname=LOCALHOST_ADDR, port=SSH_PORT):
		self.port = port
		self.hostname = LOCALHOST_ADDR

		self.channel = None
		self.session = libssh2.Session()

		try:
			self.sock = socket.socket(AF_INET, SOCK_STREAM)
		except socket.error as error:
			print "Error: Can't create socket.\n\t--> with message: %s" % (
					error)
			sys.exit(1)

		self._prepare_sock()
		self.listen()
		self.waiting_connection()

	def start_client(self, sock):
		SSHClient('xod', 'xgxzpqkux953369', sock=sock)

	def startup(self, client_sock):
		try:
			self.session.set_banner()
			self.session.startup(client_sock)
		except libssh2.SessionException, e:
			print "Error: Can't startup session: %s" % e
			sys.exit(1)		

	def _prepare_sock(self):
		try:
			self.sock.bind((self.hostname, self.port))
		except socket.error as error:
			print "Error: Failed to bind on %s:%s\s\t--> with message: %s" % (
					self.hostname, str(self.port), error)
			sys.exit(1)

	def listen(self):
		try:
			self.sock.listen(42)
		except socket.error as error:
			print "Error: Failed to listening on socket.\n\t--> with message: %s" % (
					error)

	def waiting_connection(self):
		sbuffer = 8192
		print "Listening for connection on port %s" % str(self.port)
		while 42:
			client, addr = self.sock.accept()
			# self.start_client(client)
			self.startup(client)

	def __del__(self):
		self.sock.close()

if __name__ == '__main__':
	server = SSHServer(port=4242)