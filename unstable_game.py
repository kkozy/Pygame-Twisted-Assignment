#!/usr/bin/python

import os
import math
import sys
import pygame
import random

from pygame.locals import *
from twisted.internet.protocol import Factory
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet import task
from twisted.internet.task import LoopingCall
from twisted.internet.defer import DeferredQueue
import cPickle as pickle
#import pickle

#data = pickle.dumps(data)

connections = dict()
is_client = sys.argv[1]
player_positions = dict()
state = "WAIT"

class Player1(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("p1.png")
		self.image = pygame.transform.scale(self.image,(50,30))
		self.rect = self.image.get_rect()
		self.orig_image = self.image	# keep original to limit resize errors
		self.rect = self.rect.move(500, 420)

	def tick(self):
		if is_client == "host":
			#gets mouse x and y positions
			mx, my = pygame.mouse.get_pos()
			px = self.rect.centerx
			py = self.rect.centery
			self.angle = (0) - math.degrees(math.atan2(my-py, mx-px))
			self.image = pygame.transform.rotate(self.orig_image, self.angle)
			self.rect = self.image.get_rect(center = (self.rect.centerx, self.rect.centery) )
		return

	def move(self):
		keys = pygame.key.get_pressed()
		if keys[K_RIGHT] and self.rect.x <= 600:
			self.rect = self.rect.move(2, 0)
		if keys[K_LEFT] and self.rect.x >= 0:
			self.rect = self.rect.move(-2, 0)
		if keys[K_UP] and self.rect.y >= 360:
			self.rect = self.rect.move(0, -2)
		if keys[K_DOWN] and self.rect.y <= 440:
			self.rect = self.rect.move(0, 2)
		return

class Player2(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("p2.png")
		self.image = pygame.transform.scale(self.image,(30,50))
		self.rect = self.image.get_rect()
		self.orig_image = self.image	# keep original to limit resize errors
		self.rect = self.rect.move(180, 420)

	def tick(self):
		if is_client == "client":
			#gets mouse x and y positions
			mx, my = pygame.mouse.get_pos()
			px = self.rect.centerx
			py = self.rect.centery
			self.angle = (-90) - math.degrees(math.atan2(my-py, mx-px))
			self.image = pygame.transform.rotate(self.orig_image, self.angle)
			self.rect = self.image.get_rect(center = (self.rect.centerx, self.rect.centery) )
		return

	def move(self):
		keys = pygame.key.get_pressed()
		if keys[K_RIGHT] and self.rect.x <= 600:
			self.rect = self.rect.move(2, 0)
		if keys[K_LEFT] and self.rect.x >= 0:
			self.rect = self.rect.move(-2, 0)
		if keys[K_UP] and self.rect.y >= 360:
			self.rect = self.rect.move(0, -2)
		if keys[K_DOWN] and self.rect.y <= 440:
			self.rect = self.rect.move(0, 2)
		return

class Enemy(pygame.sprite.Sprite):
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)

		foo = ['E1.png', 'E2.png', 'E3.png']

		self.hit_points = 10
		self.gs = gs
		self.image = pygame.image.load(str(random.choice(foo)))
		self.image = pygame.transform.scale(self.image,(30,30))
		self.rect = self.image.get_rect()
		self.orig_image = self.image	# keep original to limit resize errors
		self.rect = self.rect.move(50, 50)

	def tick(self):
		#do this thing

		return


class P_Laser(pygame.sprite.Sprite):
	def __init__(self,playx,playy,gs=None):

		fill_color = 0,255,0
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([10,10])
		self.image.fill(fill_color)
		self.rect = self.image.get_rect()
		 
		mx, my = pygame.mouse.get_pos()
		px = playx#self.rect.centerx
		py = playy#self.rect.centery

		mag = math.sqrt((mx-px)**(2) + (my-py)**(2))
		self.x_direction = 20*(mx-px)/mag
		self.y_direction = 20*(my-py)/mag

	def tick(self):

		self.rect = self.rect.move(self.x_direction, self.y_direction)
		return

class E_Laser(pygame.sprite.Sprite):
	def __init__(self, gs=None):

		fill_color = 0,255,0
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([10,10])
		self.image.fill(fill_color)
		self.rect = self.image.get_rect()

	def tick(self):

		self.rect = self.rect.move(0, 5)
		return

class GameSpace:
	def main(self):
		#1) basic initialization
		pygame.init()
		pygame.key.set_repeat(1,1)
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0
		self.screen = pygame.display.set_mode(self.size)
		
		# 2) set up game objects
		self.clock = pygame.time.Clock()

		self.is_client = is_client

		self.player1 = Player1(self)
		self.player2 = Player2(self)
		#enemies

	# 3) start game loop
	def do_the_thing(self):
		#print "doing the thing"
		#while
		#4) regulate tick speed is done in the game class
		
		#5) handle user input events
		#print state
		if state != "WAIT":
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN and is_client == "host":
					self.player1.move()
					#connections['GAME'].transport.write(str(event.key))
				elif event.type == pygame.KEYDOWN and is_client == "client":
					self.player2.move()
					#connections['GAME'].transport.write(str(event.key))

				if event.type == pygame.QUIT:
					reactor.stop()
					sys.exit()

			#6) ongoing behavior, send everything a tick
			self.player1.tick()
			self.player2.tick()
			#7) animations
			player_positions["p1_rect"] = self.player1.rect
			player_positions["p1_size"] = self.player1.image.get_rect().size
			player_positions["p1_image"] = pygame.image.tostring(self.player1.image, "RGB")
			player_positions["p2_rect"] = self.player2.rect
			player_positions["p2_size"] = self.player2.image.get_rect().size
			player_positions["p2_image"] = pygame.image.tostring(self.player2.image, "RGB")
			#player_positions["gamespace"] = self
			connections['GAME'].transport.write((pickle.dumps(player_positions)))
			self.screen.fill(self.black)
			if is_client == "client":
				self.screen.blit(self.player1.image, self.player1.rect)
				self.screen.blit(self.player2.image, self.player2.rect)
			elif is_client == "host":
				self.screen.blit(self.player2.image, self.player2.rect)
				self.screen.blit(self.player1.image, self.player1.rect)
			pygame.display.flip()
		else:
			return

class Game(Protocol):
	def __init__(self, users):
		self.users = users
		self.queue = DeferredQueue()
		
	def connectionMade(self):
		global state
		connections['GAME'] = self
		state = "GO"
		#print state

	def dataReceived(self, data):
		#print data
		self.queue.put(data)
		#new_gamespace = pickle.loads(data)
		#gs = new_gamespace["gamespace"]
		self.queue.get().addCallback(self.ForwardData)
			
	def ForwardData(self, data):
		positions = pickle.loads(data)
		if is_client == "host":
			gs.player2.rect = positions["p2_rect"]
			gs.player2.image = pygame.image.frombuffer(positions["p2_image"], positions["p2_size"], "RGB")
		else:
			gs.player1.rect = positions["p1_rect"]
			gs.player1.image = pygame.image.frombuffer(positions["p1_image"], positions["p1_size"], "RGB")
		if self.queue.waiting > 0:
				self.queue.get().addCallback(self.ForwardData)

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
	gs = GameSpace()
	gs.main()

	random.seed()

	if sys.argv[1] == "host":
		lc = task.LoopingCall(gs.do_the_thing)
		lc.start(0.02)
		reactor.listenTCP(8000, GameFactory())
		reactor.run() 
	elif sys.argv[1] == "client":
		lc = task.LoopingCall(gs.do_the_thing)
		lc.start(0.02)
		reactor.connectTCP('localhost', 8000, GameFactory())
		reactor.run() 
