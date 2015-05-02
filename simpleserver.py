#!/usr/bin/python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


from twisted.internet import reactor, protocol

import sys
import os
import math
import pygame
from pygame.locals import *

class Echo(protocol.Protocol):
#"""This is just about the simplest possible protocol"""
	def __init__(self):
		self.users = {}
		self.con_count = 0
		self.state = "WAITING"

	def connectionMade(self):
		print "new connection"
		self.con_count += 1
		print self.con_count

	def dataReceived(self, data):
		"As soon as any data is received, write it back."
		self.transport.write(data)


def main():
	"""This runs the protocol on port 8000"""
	factory = protocol.ServerFactory()
	factory.protocol = Echo
	reactor.listenTCP(8000,factory)
	reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
	main()