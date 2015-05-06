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
import pickle

connections = dict()
is_client = sys.argv[1]
player_positions = dict()
laser_positions = dict()
positions = dict()
state = "WAIT"



class Player1(pygame.sprite.Sprite):		#player 1 sprite
	def __init__(self, gs=None):
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("p1.png")	#different image and start position than player 2
		self.image = pygame.transform.scale(self.image,(50,30))		# resize for appropriate sprite
		self.rect = self.image.get_rect()
		self.orig_image = self.image	# keep original to limit resize errors
		self.rect = self.rect.move(150, 420)
		self.angle = 0

	def tick(self):	# on tick, each player will change their image rotation 
		if is_client == "host":
			#gets mouse x and y positions
			mx, my = pygame.mouse.get_pos()	#gets mouse position
			px = self.rect.centerx
			py = self.rect.centery
			self.angle = (0) - math.degrees(math.atan2(my-py, mx-px))
			self.image = pygame.transform.rotate(self.orig_image, self.angle)
			self.rect = self.image.get_rect(center = (self.rect.centerx, self.rect.centery) )
			#changes the angle, image, and rect so that we now face the mouse
		return

	def move(self):		#moves based on key input
		keys = pygame.key.get_pressed()
		if keys[K_RIGHT] and self.rect.x <= 600:	#doesn't let user move outside of screen area
			self.rect = self.rect.move(2, 0)
		if keys[K_LEFT] and self.rect.x >= 0:		#each key has it's own detection case
			self.rect = self.rect.move(-2, 0)
		#if keys[K_UP] and self.rect.y >= 360:
		#	self.rect = self.rect.move(0, -2)
		#if keys[K_DOWN] and self.rect.y <= 440:
		#	self.rect = self.rect.move(0, 2)
		return

class Player2(pygame.sprite.Sprite):		#basically the same as player 1
	def __init__(self, gs=None):			#different image and start position
		pygame.sprite.Sprite.__init__(self)
		self.gs = gs
		self.image = pygame.image.load("p2.png")
		self.image = pygame.transform.scale(self.image,(30,50))
		self.rect = self.image.get_rect()
		self.orig_image = self.image	# keep original to limit resize errors
		self.rect = self.rect.move(450, 420)
		self.angle = 0

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
		#if keys[K_UP] and self.rect.y >= 360:
		#	self.rect = self.rect.move(0, -2)
		#if keys[K_DOWN] and self.rect.y <= 440:
		#	self.rect = self.rect.move(0, 2)
		return

class P1_Laser(pygame.sprite.Sprite):		#the player 1 spawned laser object
	def __init__(self,playx,playy, mx, my, gs=None):

		#client and host have different colors
		fill_color = 0,255,0
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([5,5])		#laser is just a small box
		self.image.fill(fill_color)
		self.rect = self.image.get_rect()
		 
		#mx, my = pygame.mouse.get_pos()	#gets the mouse position

		mag = math.sqrt((mx-playx)**(2) + (my-playy)**(2))	#normalizes the magnitude of the lasers vector
		self.x_direction = 20*(mx-playx)/mag				#Defines the rate of x change
		self.y_direction = 20*(my-playy)/mag				#defines the rate of y change

	def tick(self):
		#every tick, the player laser will move in the defined direcitons without change
		self.rect = self.rect.move(self.x_direction, self.y_direction)
		return

class P2_Laser(pygame.sprite.Sprite):		#the player 2 spawned laser object
	def __init__(self,playx,playy,mx,my,gs=None):

		#client and host have different colors
		fill_color = 255,0,0
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([5,5])		#laser is just a small box
		self.image.fill(fill_color)
		self.rect = self.image.get_rect()
		 
		#mx, my = pygame.mouse.get_pos()	#gets the mouse position

		mag = math.sqrt((mx-playx)**(2) + (my-playy)**(2))	#normalizes the magnitude of the lasers vector
		self.x_direction = 20*(mx-playx)/mag				#Defines the rate of x change
		self.y_direction = 20*(my-playy)/mag				#defines the rate of y change

	def tick(self):
		#every tick, the player laser will move in the defined direcitons without change
		self.rect = self.rect.move(self.x_direction, self.y_direction)
		return

class Enemy(pygame.sprite.Sprite):		# this is our enemy class
	def __init__(self,xpos,ypos, direction,gs=None):
		pygame.sprite.Sprite.__init__(self)

		foo = ['E1.png', 'E2.png', 'E3.png']	#enemy image option list

		#bar = ['LEFT','RIGHT']		#randomly chooses an initial movement direction
		self.direction = direction#str(random.choice(bar))

		self.hit_points = 50			#each starts with it's own hitpoint tracker
		self.gs = gs
		self.image = pygame.image.load(str(random.choice(foo)))	#randomly chooses it's image from 3 options
		self.image = pygame.transform.scale(self.image,(30,30))	#standard resize
		self.rect = self.image.get_rect()
		self.orig_image = self.image	# keep original to limit resize errors
		self.rect = self.rect.move(xpos, ypos)

	def tick(self):	# when we tick, we move in the direction indicated by our directon var

		if self.direction == "LEFT" and self.rect.x <= 5:	#this checks to make sure the enemy won't
				self.direction = "RIGHT"					#run off the edge
		elif self.direction == "RIGHT" and self.rect.x >= 570:		#if it's about to, we change our direction
				self.direction = "LEFT"

		if self.direction == "LEFT":		#the enemy moves in the direction indicated
			self.rect = self.rect.move(-1, 0)
		elif self.direction == "RIGHT":
			self.rect = self.rect.move(1, 0)
		return

class E_Laser(pygame.sprite.Sprite): #enemy spawned laser class
	def __init__(self, xpos, ypos, gs=None):

		fill_color = 255,255,0		#has it's own laser color
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([3,8])
		self.image.fill(fill_color)
		self.rect = self.image.get_rect()
		self.rect = self.rect.move(xpos, ypos)

	def tick(self):
		#enemy lasers move downward at a rate of 15
		self.rect = self.rect.move(0, 15)
		return

class GameSpace:
	def main(self):
		#1) basic initialization
		pygame.init()
		pygame.key.set_repeat(1,1)
		self.size = self.width, self.height = 640, 480
		self.black = 0, 0, 0
		self.screen = pygame.display.set_mode(self.size)
		
		self.x = 0
		self.y = 0
		self.enemy_x_list = []
		self.enemy_y_list = []
		self.enemy_direction_list = []
		self.num_enemy = 0
		self.new_enemy = False

		# 2) set up game objects
		#self.clock = pygame.time.Clock()

		self.is_client = is_client

		self.player1 = Player1(self)
		self.player2 = Player2(self)
		#enemies

		self.all_sprites_list = pygame.sprite.Group()
		self.all_sprites_list.add(self.player1)#add player1 and player 2 to sprite list
		self.all_sprites_list.add(self.player2)

		self.laser_list1 = pygame.sprite.Group()	#laser lists for player 1 and player 2
		self.laser_list2 = pygame.sprite.Group()

		self.is_firing = False

		self.enemy_list = pygame.sprite.Group()
		self.foo = ['LEFT','RIGHT']

	# 3) start game loop
	def do_the_thing(self):

		#4) regulate tick speed is done in the game class
		
		#5) handle user input events
		#print state
		if state != "WAIT":

			if self.num_enemy == 0 and is_client == "host":
				for i in range(0,1):
					self.num_enemy +=1
					self.x = random.randint(5,605)
					self.y = random.randint(5,270)
					self.direction = str(random.choice(self.foo))
					self.enemy = Enemy(self.x,self.y,self.direction)
					self.all_sprites_list.add(self.enemy)
					self.enemy_list.add(self.enemy)
					self.enemy_x_list.append(self.x)
					self.enemy_y_list.append(self.y)
					self.enemy_direction_list.append(self.direction)
					self.new_enemy = True

			for event in pygame.event.get():
				if event.type == KEYDOWN:
					if is_client == "host":
						self.player1.move()
						#connections['GAME'].transport.write(str(event.key))
					if is_client == "client":
						self.player2.move()
						#connections['GAME'].transport.write(str(event.key))

				click1,click2,mouse = pygame.mouse.get_pressed()
				self.mx, self.my = pygame.mouse.get_pos()	#gets the mouse position
				if click1 and is_client == "host":
					self.laser = P1_Laser( self.player1.rect.centerx, self.player1.rect.centery,self.mx,self.my,self)
					self.laser.rect.x = self.player1.rect.centerx
					self.laser.rect.y = self.player1.rect.centery
					# Add the laser to the lists						
					self.laser_list1.add(self.laser)
					self.all_sprites_list.add(self.laser)
					self.is_firing = True

				if click1 and is_client == "client":
					self.laser = P2_Laser( self.player2.rect.centerx, self.player2.rect.centery,self.mx,self.my,self)
					self.laser.rect.x = self.player2.rect.centerx
					self.laser.rect.y = self.player2.rect.centery
					# Add the laser to the lists
					self.laser_list2.add(self.laser)
					self.all_sprites_list.add(self.laser)
					self.is_firing = True

				if event.type == pygame.QUIT:
					reactor.stop()
					sys.exit()
					self.is_firing = True

			#6) ongoing behavior, send everything a tick
			for item in self.laser_list1:
				item.tick()
				if item.rect.x > 700 or item.rect.x < -5 or item.rect.y > 500 or item.rect.y < -5:
					self.laser_list1.remove(item)
					self.all_sprites_list.remove(item)
			for item in self.laser_list2:
				item.tick()
				if item.rect.x > 700 or item.rect.x < -5 or item.rect.y > 500 or item.rect.y < -5:
					self.laser_list1.remove(item)
					self.all_sprites_list.remove(item)
			for item in self.enemy_list:
				item.tick()

			self.player1.tick()
			self.player2.tick()
			
			#Detect Sprite/enemy Collisions:
			for enemy in self.enemy_list:	#for first list of lasers
				for laser in self.laser_list1:
					# See if it hit the enemy
					self.hit_list1 = pygame.sprite.spritecollide(enemy, self.laser_list1, True)
		
					for hit in self.hit_list1:
						self.laser_list1.remove(laser)
						self.all_sprites_list.remove(laser)
						enemy.hit_points -= 1
						print "HP: " + str(enemy.hit_points)
						if enemy.hit_points <= 0:
							self.enemy_list.remove(enemy)
							self.all_sprites_list.remove(enemy)
							self.num_enemy -=1
							print "E# " + str(self.num_enemy)
			for enemy in self.enemy_list:	#for second list of lasers
				for laser in self.laser_list2:
					# See if it hit the enemy
					self.hit_list2 = pygame.sprite.spritecollide(enemy, self.laser_list2, True)
		
					for hit in self.hit_list2:
						self.laser_list2.remove(laser)
						self.all_sprites_list.remove(laser)
						enemy.hit_points -= 1
						print "HP: " + str(enemy.hit_points)
						if enemy.hit_points <= 0:
							self.enemy_list.remove(enemy)
							self.all_sprites_list.remove(enemy)
							self.num_enemy -=1
							print "E# " + str(self.num_enemy)
			if self.num_enemy <= 0:
				self.enemy_x_list = []
				self.enemy_y_list = []
				self.ememy_d_list = []
				self.num_ememy = 0
				print "I AM HERE AND #E IS " + str(self.num_enemy)

			#7) animations
			player_positions["p1_rect"] = self.player1.rect
			player_positions["p1_angle"] = self.player1.angle
			player_positions["p2_rect"] = self.player2.rect
			player_positions["p2_angle"] = self.player2.angle
			player_positions["mouse_x"] = self.mx
			player_positions["mouse_y"] = self.my
			player_positions["firing"] = self.is_firing
			player_positions["enemy_x"] = self.enemy_x_list
			player_positions["enemy_y"] = self.enemy_y_list
			player_positions["enemy_d"] = self.enemy_direction_list
			player_positions["spawning"] = self. new_enemy
			connections['GAME'].transport.write((pickle.dumps(player_positions)))
			self.is_firing = False
			self.new_enemy = False
			#for laser in laser_list1:
				#laser_positions["laser_rect
			self.screen.fill(self.black)

			for item in self.all_sprites_list:
				self.screen.blit(item.image,item.rect)

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
		self.flag = True

	def dataReceived(self, data):
		self.queue.put(data)
		self.queue.get().addCallback(self.ForwardData)
			
	def ForwardData(self, data):
		positions = pickle.loads(data)
		if is_client == "host":
			gs.player2.rect = positions["p2_rect"]
			gs.player2.image = pygame.transform.rotate(gs.player2.orig_image, positions["p2_angle"])
			if positions["firing"] == True:
				mx = positions["mouse_x"]
				my = positions["mouse_y"]
				self.laser = P2_Laser(gs.player2.rect.centerx, gs.player2.rect.centery,mx,my,gs)
				self.laser.rect.x = gs.player2.rect.centerx
				self.laser.rect.y = gs.player2.rect.centery
				# Add the laser to the lists
				gs.laser_list2.add(self.laser)
				gs.all_sprites_list.add(self.laser)
		else:
			gs.player1.rect = positions["p1_rect"]
			gs.player1.image = pygame.transform.rotate(gs.player1.orig_image, positions["p1_angle"])
			if positions["firing"] == True:
				mx = positions["mouse_x"]
				my = positions["mouse_y"]
				self.laser = P1_Laser(gs.player1.rect.centerx, gs.player1.rect.centery,mx,my,gs)
				self.laser.rect.x = gs.player1.rect.centerx
				self.laser.rect.y = gs.player1.rect.centery
				# Add the laser to the lists
				gs.laser_list1.add(self.laser)
				gs.all_sprites_list.add(self.laser)
			if positions["spawning"] == True:
				for i in range(0,len(positions["enemy_x"])):
					self.num_enemy +=1
					self.x = positions["enemy_x"][i]
					self.y = positions["enemy_y"][i]
					self.d = positions["enemy_d"][i]
					self.enemy = Enemy(int(self.x),int(self.y),self.d)
					gs.all_sprites_list.add(self.enemy)
					gs.enemy_list.add(self.enemy)
				
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
