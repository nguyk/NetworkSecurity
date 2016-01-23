#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import libssh2

from socket import AF_INET, SOCK_STREAM

DEBUG = True

SSH_PORT = 22
LOCALHOST_ADDR = '127.0.0.1'

def trace_session(session):
	if DEBUG and session:
		session.set_trace(
        	libssh2.LIBSSH2_TRACE_TRANS |
			libssh2.LIBSSH2_TRACE_CONN |
			libssh2.LIBSSH2_TRACE_AUTH |
			libssh2.LIBSSH2_TRACE_ERROR
		)

def debug_print(args):
	if DEBUG: print(args)

class SSHClient(object):
	def __init__(self, 
				 username,
				 password,
				 hostname=LOCALHOST_ADDR,
				 port=SSH_PORT
				):

		self.username = username
		self.password = password
		self.hostname = hostname
		self.port = port

		self.channel = None
		self.session = libssh2.Session()

		try:
			self.sock = socket.socket(AF_INET, SOCK_STREAM)
		except Exception, e:
			print "Error: Can't connect socket to (%s:%d): %s" % (
				hostname, port, e)
			sys.exit(1)

		self.connect()
		self.startup()
		self.authenticate()
		self.open_session()

	def authenticate(self):
		try:
			self.session.userauth_password(self.username, self.password)
		except SessionException, e:
			print "Error: Failed to authenticate user ({0})\
				with this password.".format(self.username)
			sys.exit(1)

	def connect(self):
		try:
			self.sock.connect((self.hostname, self.port))
		except Exception, e:
			print str(e)
			raise Exception, self.session.last_error()

	def startup(self):
		try:
			self.session.set_banner()
			trace_session(self.session)
			self.session.startup(self.sock)
		except SessionException, e:
			print "Error: Can't startup session: %s" % e
			sys.exit(1)

	def open_session(self):
		try:
			self.channel = self.session.open_session()
		except Exception, e:
			print str(e)
			raise Exception, self.session.last_error()

	def execute(self, command='uname -a'):
		_buffer = 4096
		read_channel = self.channel.execute(command)
		debug_print(read_channel)
		while True:
			data = self.channel.read(_buffer)
			if data == '' or data == None: break
			debug_print(type(data))
			print data.strip()
		self.channel.close()

	def __del__(self):
		self.session.close()
		debug_print(self.session.last_error())

if __name__ == '__main__':
	client = SSHClient('xod', 'xgxzpqkux953369=a')
	client.execute('ls -la')