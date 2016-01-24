#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import libssh2
import subprocess
import select, sys
import tty, termios

from socket import AF_INET, SOCK_STREAM, AF_UNIX, SHUT_RDWR

DEBUG = False

SSH_PORT = 22
LOCALHOST_ADDR = '127.0.0.1'

x11_channels = []

def raw_mode(fd):
	tty.setraw(fd)

def x11_callback(session, channel, shost, sport, abstract):
	display = os.environ["DISPLAY"]
	display_port = display[display.index(":")+1]
	_path_unix_x = "/tmp/.X11-unix/X%s" % display_port
	if display[:5] == "unix:" or display[0] == ':':
		sock = socket.socket(AF_UNIX, SOCK_STREAM)
		sock.connect(_path_unix_x)
	channel.setblocking(0)
	x11_channels.append((sock, channel))

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

		self.fd = sys.stdin.fileno()
		self.old_settings = termios.tcgetattr(self.fd)

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
			self.session.callback_set(libssh2.LIBSSH2_CALLBACK_X11, x11_callback)
		except SessionException, e:
			print "Error: Can't startup session: %s" % e
			sys.exit(1)

	def open_session(self):
		sbuffer = 8192
		try:
			self.channel = self.session.open_session()
			self.channel.pty('xterm')
			p = subprocess.Popen(['xauth', 'list'], shell=False, stdout=subprocess.PIPE)
			xauth_data = p.communicate()[0]
			auth_protocol, auth_cookie = xauth_data.split()[1:3]
			self.channel.x11_req(0, auth_protocol, auth_cookie, 0)
			self.channel.shell()
			self.channel.setblocking(0)
			raw_mode(self.fd)

			while True:
				socks = [self.fd] + [sock for sock, _ in x11_channels]
				r, w, x = select.select(socks, [], [], 0.01)
				status, data = self.channel.read_ex(sbuffer)
				
				if status > 0:
					sys.stdout.write(data)
				else:
					sys.stdout.flush()

				for sock, x11_chan in x11_channels:
					status, data = x11_chan.read_ex(sbuffer)
					if status > 0:
						sock.sendall(data)

					if sock in r:
						data = sock.recv(sbuffer)
						if data is None:
							sock.shutdown(SHUT_RDWR)
							sock.close()
							x11_channels.remove((x11_chan, sock))
						else:
							x11_chan.write(data)

					if x11_chan.eof():
						sock.shutdown(SHUT_RDWR)
						sock.close()
						x11_channels.remove((x11_chan, sock))
						continue

				if self.channel.eof():
					break

		except libssh2.ChannelException, e:
			print "Error: Channel exception: %s" % e
		finally:
			self.channel.close()

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
	# client.execute('ls -la')