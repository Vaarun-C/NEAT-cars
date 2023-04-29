import math
import pygame
import pygame.gfxdraw
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
max_fit = 1000

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
		self.checkpoints = set()
	
	def reset(self):
		print(f'reset!{self}')
		super().reset()
		self.fitness = 0
		self.set_alive(True)

	def calc_fitness(self):
		# self.fitness += self.speed*(time.time()-self.temp_time)
		self.fitness = len(checkpoints)
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
		# self.binary_matrix = [[0]*screen_width]*screen_height
		# self.distance_matrix = [[0]*screen_width]*screen_height
		# self.mask = pygame.mask.from_surface(self.image)
		self.checkpoints = []
		self.checkpointsMade = False
		# self.inc = 5

	def draw(self):
		screen.blit(self.image, (0,0))
		if not self.checkpointsMade:
			self.makeCheckpoints()
			self.checkpointsMade = True

		if self.checkpointsMade:
			for row in self.checkpoints[::20]:
				for e in range(len(row)-1)[::2]:
					# pygame.draw.line(screen, red, row[e], row[e+1])
					# pygame.draw.circle(screen, red, row[e], 5, 0)
					# pygame.draw.circle(screen, red, row[e+1], 5, 0)
					# print(abs(row[e+1][0] - row[e][0]), row[e+1][0], row[e][0])
					# if abs(row[e+1][0] - row[e][0])-30 < 5:
					if abs(row[e][0] - row[e+1][0]) <= 200:
						# print(f"\x1b[31m{row[e], row[e+1]}\x1b[0m")
						pygame.draw.line(screen, red, row[e], row[e+1])
					# else:
					# 	for f in range(abs(row[e][0] - row[e+1][0]))[::20]:
					# 		starty = row[e][1]
					# 		inc = 1
					# 		ends = []
					# 		while True:
					# 			end = [f, starty+inc]
					# 			if end[1]>screen_height:
					# 				break
					# 			end = tuple(end)
					# 			if (screen.get_at((int(end[0]), int(end[1]))) == white) or (int(end[1]) > screen_height):
					# 				ends.append(end)
					# 				break
					# 			inc += 1
					# 		inc = 1
					# 		while True:
					# 			end = [f, starty-inc]
					# 			if end[1]>screen_height:
					# 				break
					# 			end = tuple(end)
					# 			if (screen.get_at((int(end[0]), int(end[1]))) == white) or (int(end[1]) > screen_height):
					# 				ends.append(end)
					# 				break
					# 			inc += 1

					# 		if ((len(ends) == 2) and (abs(ends[0][1] - ends[1][1]) <=400)):
					# 			pygame.draw.line(screen, red, ends[0], ends[1])


				# if(self.track_pixels.index(row) == 100):
				# 	break

			# temp_screen = pygame.Surface((screen_width, screen_height))
			# pygame.draw.aalines(screen, red, False, pygame.math.bezier(self.track_pixels, 20), 2)
			# print(f"\x1b[31m{self.track_pixels}\n\n{len(self.track_pixels)}\x1b[0m")
			# pygame.gfxdraw.bezier(screen, self.track_pixels[:400], 4, red)

			# print(self.track_pixels[60])
			# quit()
			# start = 0
			
			# for row in range(len(self.track_pixels))[::5]:
			# 	try:
			# 		# print(abs(self.track_pixels[row][start][0]-self.track_pixels[row][start+30][0]))
			# 		if(abs(self.track_pixels[row][start][0]-self.track_pixels[row][start+30][0]) <= 30):
			# 			pygame.draw.line(screen, red, self.track_pixels[row][start], self.track_pixels[row][start+30])
			# 			start += 30
			# 	except IndexError:
			# 		print(self.track_pixels[row])
			# 		# quit(c)


			# quit()
			# print("DONE")

			# screen.blit(temp_screen, (0,0))
		# 	for y in range(screen_height):
		# 		for x in range(screen_width):
		# 			if(self.binary_matrix[y][x] == 1):
		# 				screen.set_at((x,y), red)

	def handleCheckpoints(self):
		for i, car in enumerate(caravan):
			point = (int(car.x + math.cos(car.angle) * car.width / 2),int(car.y + math.sin(car.angle) * car.width / 2))

			if screen.get_at(point) == red:
				pass

	def checkCollision(self):
		global caravan, dead_caravan

		for i, car in enumerate(caravan):
			point = (int(car.x + math.cos(car.angle) * car.width / 2),int(car.y + math.sin(car.angle) * car.width / 2))

			if screen.get_at(point) == white:
				car.set_alive(False)
				caravan.pop(i)
				dead_caravan.append(car)

	# def neighbours(self, x, y, image):
	# 	img = image
	# 	x_1, y_1, x1, y1 = x-1, y-1, x+1, y+1
	# 	return [ img[x_1][y], img[x_1][y1], img[x][y1], img[x1][y1], img[x1][y], img[x1][y_1], img[x][y_1], img[x_1][y_1] ]

	# def transitions(self, neighbours):
	# 	n = neighbours + neighbours[0:1]
	# 	print(n)
	# 	return sum( (n1, n2) == (0, 1) for n1, n2 in zip(n, n[1:]) )

	def makeCheckpoints(self):
		# self.pixel_array = pygame.PixelArray(self.image)
		# for y in range(screen_height):
		# 	for x in range(screen_width):
		# 		print((x,y))
		# 		if screen.get_at((x,y)) == black:
		# 			self.track_pixels.append((x, y))

		for y in range(screen_height):
			row = []
			start = False
			for x in range(screen_width):
				if(screen.get_at((x,y)) == black) and not start:
					# self.binary_matrix[y][x] = 1
					row.append((x,y))
					start = True

				if(screen.get_at((x,y)) != black) and start:
					row.append((x,y))
					start = False

					# row.append((x,y))
			# print(row)
			self.checkpoints.append(row)

		# dist_matrix = [[0 for j in range(size)] for i in range(size)]

		# Compute Euclidean distance transform
		# for i,j in one_coords:
		# 	min_dist = math.inf
		# 	for k in range(size):
		# 		for l in range(size):
		# 			if matrix[k][l] == 0:
		# 				dist = math.sqrt((i-k)**2 + (j-l)**2)
		# 				if dist < min_dist:
		# 					min_dist = dist
		# 	dist_matrix[i][j] = min_dist
		# changing1 = changing2 = 1
		# while changing1 or changing2:

		# 	changing1 = []
		# 	rows, columns = screen_height, screen_width
		# 	for x in range(1, rows - 1):
		# 		for y in range(1, columns - 1):

		# 			P2,P3,P4,P5,P6,P7,P8,P9 = n = self.neighbours(x, y, self.binary_matrix)
		# 			if ((self.binary_matrix[x][y] == 1) and (2 <= sum(n) <= 6) and (self.transitions(n) == 1) and (P2 * P4 * P6 == 0) and (P4 * P6 * P8 == 0)):         # Condition 4
						
		# 				changing1.append((x,y))
		# 	for x, y in changing1: 
		# 		self.binary_matrix[x][y] = 0

		# 	changing2 = []
		# 	for x in range(1, rows - 1):
		# 		for y in range(1, columns - 1):
		# 			P2,P3,P4,P5,P6,P7,P8,P9 = n = self.neighbours(x, y, self.binary_matrix)
		# 			if ((self.binary_matrix[x][y] == 1) and (2 <= sum(n) <= 6) and (self.transitions(n) == 1) and (P2 * P4 * P8 == 0) and (P2 * P6 * P8 == 0)):            # Condition 4
		# 				changing2.append((x,y))    
			
		# 	for x, y in changing2: 
		# 		self.binary_matrix[x][y] = 0
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
				if(car.fitness >= max_fit):
					running = False
					break
				parents.append(car)
				dead_caravan.remove(car)

				print(f"\x1b[32m=======BEST CAR {parents[-1]}========\x1b[0m")
				print(f"\x1b[32mBest Score: {parents[-1].fitness}\x1b[0m")
			
			caravan = neat.newPopulation(parents, dead_caravan+parents)
			dead_caravan = []
			generation+=1
		else:

			# draw cars
			for car in caravan:
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

if __name__ == '__main__':
	main()