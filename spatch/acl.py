#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sys

class Acl(object):
	def __init__(self, filepath='spatch.right'):
		try:
			with open(filepath, 'r') as csv_file:
				reader = csv.reader(csv_file, delimiter='|')
				self.acl = self.parse(reader)
		except:
			sys.exit(1)

	def parse(self, reader):
		acl_dict = {}
		for row in reader:
			if row[0] not in acl_dict.keys():
				acl_dict[row[0]] = {'allowed_servers': [], 'servers_rights': []}
			acl_dict[row[0]]['passwd'] = row[1]
			acl_dict[row[0]]['allowed_servers'].append(row[2])
			acl_dict[row[0]]['servers_rights'].append((row[3], row[4], row[5]))
		return acl_dict

	def get(self, **kwargs):
		if 'username' in kwargs.keys():
			if kwargs['username'] in self.acl.keys():
				return self.acl[kwargs['username']]
		return self.acl

	def check_user(self, username, passwd):
		if username in self.acl.keys():
			if passwd == self.acl[username]['passwd']:
				return True
		return False

	def get_user_allowed_servers(self, username):
		if username in self.acl.keys():
			return self.acl[username]['allowed_servers']

	def get_user_right_on_server(self, username, server_addr):
		if username in self.acl.keys():
			if server_addr in self.acl[username]['allowed_servers']:
				return self.acl[username]['servers_rights'][self.acl[username]['allowed_servers'].index(server_addr)]
		return None

if __name__ == '__main__':
	acl = Acl()