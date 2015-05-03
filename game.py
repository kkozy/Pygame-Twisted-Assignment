#!/usr/bin/python

import os
import math
import sys
import pygame
from pygame.locals import *

from twisted.internet.protocol import Factory
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol

from twisted.internet import reactor
from twisted.internet import protocol

class GameSpace:
	def main(self):
		#1) basic initialization
		pygame.init()
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0
		self.screen = pygame.display.set_mode(self.size)
		
		# 2) set up game objects
		self.clock = pygame.time.Clock()
		self.player1 = Player(self)
		self.player2 = Player(self)
		#enemies

	def do_the_thing(self):	# 3) start game loop
		print "doing the thing"
		#while
			#4) regulate tick speed
			#5) handle user input events
			#6) ongoing behavior, send everything a tick
			#7) animations

class Game(Protocol):
	def __init__(self, users):
		self.users = users
		self.player_number = is_client + 1
	

	def connectionMade(self):
		message = "hello"
		self.transport.write(message)
		print "CONNECTION MADE"
		#print is_client
		print "You are Player " + str(self.player_number)
		#if is_client == 0:
			#go send infor
		#if is_client == 1:
			#otherwise you wait


	def dataReceived(self, data):
		print data

	def connectionLost(self,reason):
		print "Connection lost - goodbye!"
		reactor.stop()
	def clientConnectionLost(self, reason):
		print "Connection lost - goodbye!"
		reactor.stop()

class GameFactory(ClientFactory):
	def __init__(self):
		self.users = {}

	def buildProtocol(self, addr):
		return Game(self.users)



if __name__ == "__main__":
	#gs = GameSpace()
	if sys.argv[1] == "host":
		reactor.listenTCP(8000, GameFactory())
		is_client = 0
		reactor.run() 
	elif sys.argv[1] == "client":
		reactor.connectTCP('localhost', 8000, GameFactory())
		is_client = 1
		reactor.run() 