#Library Imports
import math
import pygame
import time
from NeuralNetwork import NN
from NEAT import NEAT 

# initialize pygame
pygame.init()

# set up the game screen
screen = pygame.display.set_mode()
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Car Race Game")

#fonts
generation_font = pygame.font.SysFont("Arial", 40)
font = pygame.font.SysFont("Arial", 30)

# set up the clock
clock = pygame.time.Clock()

#Stop when this fitness is reached
max_fit = 200

# define colors
black = (0, 0, 0, 255)
white = (255, 255, 255, 255)
red = (255, 0, 0, 255)
green = (0, 255, 0, 255)
blue = (0, 0, 255, 255)

# GLOBALS
track_img_path = "track.png"
running = False
caravan = []
dead_caravan = []
UP = 0
RIGHT = 1
DOWN = 3
LEFT = 2
FAIL =-1
PI = math.pi
no_parents = 2
pop_size = 100

# define Sensor class
class Sensor:
	def __init__(self, car):
		self.numRays = 5
		self.spread = PI
		self.rays = []
		self.car = car
		self.readings = []
		self.angle = 0

	def lerp(self, a, b, t):
		return a+(b-a)*t

	def getDistance(self, p0, p1):
		self.readings.append(((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2)**0.5)

	def update(self):
		self.rays = []
		self.readings = []
		for i in range(self.numRays):
			self.angle = self.lerp(self.spread/2, -self.spread/2, i/((1/2) if self.numRays == 1 else (self.numRays-1))) + self.car.angle + PI

			start = (self.car.x, self.car.y)
			inc = 1
			while True:
				end = [self.car.x-math.cos(self.angle)*inc, self.car.y-math.sin(self.angle)*inc]
				if end[0]<0: end[0] = 0
				if end[0]>screen_width: end[0] = screen_width-5
				if end[1]<0: end[1] = 0
				if end[1]>screen_height: end[1] = screen_height-5
				end = tuple(end)
				if (screen.get_at((int(end[0]), int(end[1]))) != black) or (int(end[0]) > screen_width) or (int(end[1]) > screen_height):
					break
				inc += 1

			self.rays.append((start, end))
			self.getDistance(start, end)

		self.car.dist = self.readings

	def draw(self):
		for i, ray in enumerate(self.rays):
			pygame.draw.line(screen, green, ray[0], ray[1])

# define Car class
class Car:
	def __init__(self, x, y, image):
		self.start = x,y
		self.x = x
		self.y = y
		self.image = image
		self.width = image.get_width()
		self.height = image.get_height()
		self.speed = 5
		self.acceleration = 0.1
		self.max_speed = 100
		self.angle = PI/2
		self.rotate_speed = 1
		self.max_angle = 45
		self.alive = True

	def update(self, direc):
		if direc == UP:
			self.speed += self.acceleration
			if self.speed > self.max_speed:
				self.speed = self.max_speed

		# elif direc == DOWN:
		# 	self.speed -= self.acceleration
		# 	if self.speed < -self.max_speed:
		# 		self.speed = -self.max_speed
		
		# handle car rotation
		if direc == RIGHT: self.angle += 0.05
		elif direc == LEFT: self.angle -= 0.05
		if self.angle >PI: self.angle -=2*PI
		if self.angle <-PI: self.angle +=2*PI
		
		# update car position
		self.x += self.speed * math.cos(self.angle)
		self.y += self.speed * math.sin(self.angle)

		# wrap-around
		if self.x < -self.width:     self.x = screen_width
		elif self.x > screen_width:  self.x = -self.width
		if self.y < -self.height:    self.y = screen_height
		elif self.y > screen_height: self.y = -self.height
		return self
	
	def reset(self):
		# print(f'reset!{self}')
		self.x, self.y = self.start
		self.speed = 5
		self.acceleration = 0.1
		self.max_speed = 100
		self.angle = PI/2
		self.rotate_speed = 1
		self.max_angle = 45
		self.checkpoints = set()
		self.fitness = 0

	def draw(self):
		rotated_image = pygame.transform.rotate(self.image, -self.angle*180/math.pi)
		screen.blit(rotated_image, (self.x - rotated_image.get_width()/2, self.y - rotated_image.get_height()/2))
		return self
	
	def get_alive(self):
		return self.alive

	def set_alive(self, val):
		self.alive = val

	def __repr__(self) -> str:
		return f"Car({self.x},{self.y})"

# define Player class
class Player(Car):
	def __init__(self, x, y, image):
		Car.__init__(self, x, y, image)
		self.speed = 0
	
	def update(self):
		# update car position
		direc = FAIL
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP]: direc = UP
		elif keys[pygame.K_DOWN]: direc = DOWN
		if keys[pygame.K_RIGHT]: direc = RIGHT
		elif keys[pygame.K_LEFT]: direc = LEFT        
		return super().update(direc)
	
	def draw(self):
		if not self.get_alive():
			print("You have died")
		else:
			return super().draw()
	
	def __repr__(self) -> str:
		return f"You({self.x},{self.y})"

# define Computer class
class Computer(Car):
	id = 0
	def __init__(self, x, y, image):
		self.dist = [0,0,0,0,0] # W NW N NE E
		self.brain = NN([5, 6, 3])
		self.start_time = time.time()
		self.temp_time = self.start_time
		Computer.id += 1
		self.id = Computer.id
		super().__init__(x, y, image)
		self.sensor = Sensor(self)
		self.fitness = 0
		self.controls = [LEFT, UP, RIGHT]
	
	def reset(self):
		print(f'reset!{self}')
		super().reset()
		self.set_alive(True)

	def calc_fitness(self):
		self.fitness += self.speed*(time.time()-self.temp_time)
		self.temp_time = time.time()
	
	def update(self):
		if not self.get_alive(): return
		self.sensor.update()
		direc = FAIL
		self.calc_fitness()
		direc = self.compute() # U R D L
		super().update(direc)
	
	def compute(self):
		if not self.get_alive(): return self
		outputs = self.brain.feedForward(self.brain, self.dist)
		return self.controls[outputs.index(max(outputs))]
	
	def draw(self):
		if not self.get_alive(): return self
		self.sensor.draw()
		return super().draw()
	
	def __repr__(self) -> str:
		return f"Comp[{self.id}]({self.x},{self.y})"

# define Track class
class Track:
	def __init__(self, image):
		self.image = image

	def draw(self):
		screen.blit(self.image, (0,0))

	def checkCollision(self):
		global caravan, dead_caravan

		for i, car in enumerate(caravan):
			point = (int(car.x + math.cos(car.angle) * car.width / 2),int(car.y + math.sin(car.angle) * car.width / 2))

			if screen.get_at(point) == white:
				car.set_alive(False)
				caravan.pop(i)
				dead_caravan.append(car)

#Main Loop
def main():

	global caravan, running, dead_caravan

	neat = NEAT()

	running = True

	car_image = pygame.image.load("car.png")
	car_image = pygame.transform.scale(car_image, (83, 30))
	track_img = pygame.image.load(track_img_path)
	track_img = pygame.transform.scale(track_img, (screen_width, screen_height))

	# Init my cars
	for i in range(pop_size):
		caravan.append(Computer(90,screen_height/2,car_image))
	# caravan.append(Player(90, screen_height/2, car_image))

	# create track object
	track = Track(track_img)
	generation = 1
	while running:

		# event loop
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False

		# draw background and track
		screen.fill(white)
		track.draw()

		track.checkCollision()


		text = generation_font.render("Generation : " + str(generation), True, blue)
		text_rect = text.get_rect()
		text_rect.center = (screen_width/2, 100)
		screen.blit(text, text_rect)

		text = font.render("Cars : " + str(len(caravan)), True, blue)
		text_rect = text.get_rect()
		text_rect.center = (screen_width/2, 230)
		screen.blit(text, text_rect)


		if len(caravan) == 0:
			parents = []
			for i in range(no_parents):
				car = max(dead_caravan, key=lambda x:x.fitness)
				parents.append(car)
				dead_caravan.remove(car)

				print(f"\x1b[32mBEST CAR {parents[-1]}\x1b[0m")
				print(f"\x1b[32mBest Score: {parents[-1].fitness}\x1b[0m")

			caravan = neat.newPopulation(parents, dead_caravan+parents)
			dead_caravan = []
			generation += 1
		else:

			# draw cars
			for car in caravan:
				if(car.fitness >= max_fit):
					running = False
					screen.fill(white)
					text = font.render(f"THE BEST CAR IS: {str(car.id)}", True, red)
					text_rect = text.get_rect()
					text_rect.center = (screen_width//2, screen_height//3)
					screen.blit(text, text_rect)
					car_image = pygame.transform.scale(car_image, (200, 72))
					screen.blit(car_image, (screen_width//2-car.width, screen_height//2))
					pygame.display.update()
					time.sleep(5)
					break
				text = font.render(str(car.id), True, red)
				text_rect = text.get_rect()
				text_rect.center = (car.x, car.y-30)
				screen.blit(text, text_rect)
				car.update()    
				car.draw()

		# update display
		pygame.display.update()

		# set frame rate    
		clock.tick(60)			
# name condition
if __name__ == '__main__':
	main()
