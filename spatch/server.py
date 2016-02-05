#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
import libssh2
import os
import threading
import traceback
import paramiko

from acl import Acl
from client import SSHClient
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from paramiko.py3compat import b, u, decodebytes

host_key = paramiko.RSAKey(filename='rsa.key')

SSH_PORT = 22
LOCALHOST_ADDR = '127.0.0.1'
allowed_servers = 'vide'
acl = Acl()

class Server (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
    	if acl.check_user(username, password):
    		return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth,
                                  pixelheight, modes):
        return True

class SSHServer(object):
	def __init__(self, hostname=LOCALHOST_ADDR, port=SSH_PORT):
		self.port = port
		self.hostname = LOCALHOST_ADDR

		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except socket.error as error:
			print "[-] Error: Can't create socket.\n\t--> with message: %s" % (
					error)
			sys.exit(1)

		self._prepare_sock()
		self.listen()
		self.waiting_connection()

	def start_client(self, sock):
		SSHClient('user', 'passwd', sock=sock)		

	def _prepare_sock(self):
		try:
			self.sock.bind((self.hostname, self.port))
		except socket.error as error:
			print "[-] Error: Failed to bind on %s:%s\s\t--> with message: %s" % (
					self.hostname, str(self.port), error)
			sys.exit(1)

	def listen(self):
		try:
			self.sock.listen(42)
		except socket.error as error:
			print "[-] Error: Failed to listening on socket.\n\t--> with message: %s" % (
					error)

	def waiting_connection(self):
		sbuffer = 8192
		print "[+] Listening for connection on port %s" % str(self.port)
		while 42:
			client, addr = self.sock.accept()
			print ("Someone connected on Spatch")
			self.ssh_init(client)

	def ssh_init(self, client_sock):
		try:
			self.ssh = paramiko.Transport(client_sock)
			self.ssh.set_gss_host(socket.getfqdn(""))
			try:
				self.ssh.load_server_moduli()
			except:
				print ("Failed in the loading process of moduli")
				sys.exit(1)
			server_machine = Server()
			self.ssh.add_server_key(host_key)
			try:
				self.ssh.start_server(server=server_machine)
			except paramiko.SSHException:
				print ("SSH start failed")
				sys.exit(1)

			try:
				chan = self.ssh.accept(20)
				print "Accept in channel"
			except Exception as e:
				print ("Error in accept")

			if chan is None:
				print("No channel")
				sys.exit(1)

			server_machine.event.wait(10)
			if not server_machine.event.is_set():
				print("Client never asked for a shell")
				sys.exit(1)

			chan.send("\rWelcome to Spatch Proxy !\n")
			chan.send("\rSelect your server:\n\r")
			allowed_servers = acl.get_user_allowed_servers()
			response = ''
			for i in range(len(allowed_servers)):
				response += "\r\n\t%s) %s" % (i, allowed_servers[i]["name"])
			response += "\n\r"
			chan.send(response)
			f = chan.makefile("rU")

			server_choice = f.readline()
			int_server_choice = -42
			while True:
				try:
					int_server_choice = int(server_choice)
				except:
					chan.send("not a number: " + server_choice + "\r")
				if int_server_choice >= 0 and int_server_choice <= i:
					chan.send("You choosed server: " + allowed_servers[int_server_choice]["name"] + "\n\r")
					while True:
						cmd = f.readline()
						# ici je récupére la commande
						chan.send("You typed command: " + cmd)
				else:
					if int_server_choice != -42:
						chan.send("invalid server choose: " + server_choice + "\r")
					server_choice = f.readline()
			chan.close()

		except Exception as e:
			print('*** Caught exception: ' + str(e.__class__) + ': ' + str(e))
			traceback.print_exc()
			try:
				self.ssh.close()
			except:
				sys.exit(1)


	def __del__(self):
		self.sock.close()

if __name__ == '__main__':
	server = SSHServer(port=4242)