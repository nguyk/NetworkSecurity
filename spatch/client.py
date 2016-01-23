#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import libssh2

DEBUG = True

SSH_PORT = 22
LOCALHOST_ADDR = '127.0.0.42'

def trace_session(session):
	if DEBUG and session:
		session.set_trace(
        	libssh2.LIBSSH2_TRACE_TRANS |
			libssh2.LIBSSH2_TRACE_CONN |
			libssh2.LIBSSH2_TRACE_AUTH |
			libssh2.LIBSSH2_TRACE_ERROR
		)

class SSHClient(object):
	LIBSSH2_ERROR_EAGAIN = -37
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

		self.session = libssh2.Session()

		self.channel = None

		try:
			self.sock = socket.socket()
		except Exception, e:
			print "Error: Can't connect socket to (%s:%d): %s" % (
				hostname, port, e)
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
		buffer = 4096


if __name__ == '__main__':
	client = SSHClient('xod', 'xgxzpqkux953369=a')
	client.connect()
	client.startup()
	client.open_session()