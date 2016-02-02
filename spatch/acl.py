#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

class Acl(object):
	def __init__(self, filepath='spatch.right'):
		self.json_acl = json.load(open(filepath, 'r'))
		self.users = [user for user in self.json_acl["users"]]
		self.servers = [server for server in self.json_acl["servers"]]


	def get(self, **kwargs):
		if 'username' in kwargs.keys():
			for user in self.users:
				if user["name"] == kwargs["username"]:
					return user
		if 'servername' in kwargs.keys():
			for server in self.servers:
				if server["name"] == kwargs["servername"]:
					return server
		return self.json_acl

	def check_user(self, username, passwd):
		for user in self.users:
			if username == user["name"] and passwd == user["password"]:
				return True
		return False

	def get_user_allowed_servers(self, username):
		for user in self.users:
			if username == user["name"]:
				return user["allowed_servers"]
		return None

	def get_user_right_on_server(self, username, servername):
		for user in self.users:
			if username == user["name"]:
				for server in user["allowed_servers"]:
					if servername == server["name"]:
						return server["rights"]
		return None

if __name__ == '__main__':
	acl = Acl()
	# print(acl.get(username="xod"))
	# print(acl.get(servername="localhost"))
	# print(acl.check_user('xod', 'testtest'))
	# print(acl.get_user_allowed_servers('xod'))
	# print(acl.get_user_right_on_server('xod', 'localhost'))