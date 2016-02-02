#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass

from acl import Acl
from spatch_client import SSHSpatchClient

acl = Acl()

if __name__ == '__main__':
	print "[+] Welcome on spatch proxy."
	username = raw_input("[+] Enter your login please (leave blank for {}): ".format(getpass.getuser()))
	if username == '':
		username = getpass.getuser()
	passwd = getpass.getpass("[+] Enter your password please : ")

	if acl.check_user(username, passwd):
		allowed_servers = acl.get_user_allowed_servers(username)
		print "[+] You have grented access to those servers on our network, make a choice :"
		i = 0
		for server in allowed_servers:
			print "{}: {}".format(i, server)
			i += 1

		choice = raw_input("Your choice : ")
		if int(choice) >= 0 and int(choice) <= len(allowed_servers)-1:
			print "[+] Your choice is {}".format(choice)
			print "[+] Connection to {}...".format(allowed_servers[int(choice)])
			SSHSpatchClient(username, passwd)
		else:
			print "[-] This choice ({}) isn't allowed sorry !".format(choice)