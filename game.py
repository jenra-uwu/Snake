##
## Snake
## game.py: Implements the main game logic.
##
## jenra
## June 19 2018
##

from random import randint, choice


def update_coordinates(direction, x, y, width, height, undo=False):
	x += ((1 if direction & 1 else -1) if ~direction & 2 else 0) * (-1 if undo else 1)
	y += ((1 if direction & 1 else -1) if  direction & 2 else 0) * (-1 if undo else 1)

	if x >= width:
		x = 0
	if x < 0:
		x = width - 1
	if y >= height:
		y = 0
	if y < 0:
		y = height - 1
	return x, y

def reverse(direction):
	return  (direction > 1) * 2 + (not (direction - (direction > 1) * 2))

class Snake:
	def __init__(self, x, y, use_ai):
		self.direction = 0
		self.moving = use_ai
		self.dead = False
		self.kp = False
		self.x = x
		self.y = y
		self.prev_dirs = [self.direction]
		self.use_ai = use_ai
		self.debug = use_ai and False

	def key_down(self, event):
		if self.kp or self.dead:
			return
		if event.keysym == 'Left' and (self.direction & 2 or not self.moving):
			self.direction = 0
			self.kp = True
			self.use_ai = False
		if event.keysym == 'Right' and (self.direction & 2 or not self.moving):
			self.direction = 1
			self.kp = True
			self.use_ai = False
		if event.keysym == 'Up' and not (self.direction & 2 and self.moving):
			self.direction = 2
			self.kp = True
			self.use_ai = False
		if event.keysym == 'Down' and not (self.direction & 2 and self.moving):
			self.direction = 3
			self.kp = True
			self.use_ai = False
		if not self.moving:
			self.moving = True

	def update_position(self, width, height):
		if self.moving:
			self.x, self.y = update_coordinates(self.direction, self.x, self.y, width, height)
			self.prev_dirs = [self.direction] + self.prev_dirs[:-1]
			self.kp = False

	def ai(self, world):
		body_dir = reverse(self.direction)
		dirs = [(body_dir + 1) % 4, (body_dir + 2) % 4, (body_dir + 3) % 4]
		valid_dirs = []

		for dir in dirs:
			x, y = update_coordinates(dir, self.x, self.y, world.width, world.height)
			if world.blocks[x][y] == 2:
				self.direction = dir
				return
			elif world.blocks[x][y] != 1:
				valid_dirs += [dir]
			else:
				fx, fy = update_coordinates(self.prev_dirs[-1], x, y, world.width, world.height, undo=True)
				ox, oy = update_coordinates((1+2+3) - reverse(self.prev_dirs[-1]) - self.direction - dir, x, y, world.width, world.height, undo=True)
				if world.blocks[fx][fy] != 1 and world.blocks[ox][oy] != 1:
					valid_dirs += [dir]

		if valid_dirs:
			dists = [None, None, None, None]
			for dir in range(4):
				x, y = update_coordinates(dir, self.x, self.y, world.width, world.height)
				dist = 1
				while world.blocks[x][y] == 0 and x != world.pellet[0] and y != world.pellet[1]:
					x, y = update_coordinates(dir, x, y, world.width, world.height)
					dist += 1
				if world.blocks[x][y] == 0 or world.blocks[x][y] == 2:
					dists[dir] = dist
			allowed = []
			for dir in range(4):
				if dists[dir]:
					allowed += [dir]
			allowed = sorted(allowed, key=lambda x: dists[x])
			if not allowed:
				self.direction = choice(valid_dirs)
			elif not self.direction in allowed:
				self.direction = allowed[0]
		elif self.debug:
			self.moving = False

	def tick(self, world):
		if self.use_ai:
			self.ai(world)
		self.update_position(world.width, world.height)



class World:
	def __init__(self, swidth, sheight, blwidth, blheight, use_ai):
		self.swidth = swidth
		self.sheight = sheight
		self.width = swidth // blwidth
		self.height = sheight // blwidth
		self.rect_width = blwidth
		self.rect_height = blheight
		self.blocks = [[0 for _ in range(self.height)] for _ in range(self.width)]
		self.snake = Snake(0, 0, use_ai)
		self.pellet = [randint(0, self.width - 1), randint(0, self.height - 1)]

	def snake_block_update(self, snake):
		x = snake.x
		y = snake.y
		if self.blocks[x][y] == 2:
			snake.prev_dirs += snake.prev_dirs[-1:]
			while True:
				self.pellet = [randint(0, self.width - 1), randint(0, self.height - 1)]
				if self.blocks[self.pellet[0]][self.pellet[1]] == 0:
					break

		first = True
		for d in snake.prev_dirs:
			if not snake.moving and not snake.dead and first:
				self.blocks[x][y] = 4
				first = False
			elif self.blocks[x][y] == 1:
				self.blocks[x][y] = 3
				snake.dead = True
				snake.moving = False
			elif self.blocks[x][y] != 3:
				self.blocks[x][y] = 1
			x, y = update_coordinates(d, x, y, self.width, self.height, undo=True)

	def tick(self):
		self.snake.tick(self)

		self.blocks = [[0 for _ in range(self.height)] for _ in range(self.width)]
		self.blocks[self.pellet[0]][self.pellet[1]] = 2

		self.snake_block_update(self.snake)

	def render(self, canvas):
		for x in range(0, self.width):
			for y in range(0, self.height):
				if self.blocks[x][y]:
					fill = '#FFFF00' if self.blocks[x][y] == 1 else '#00FF00' if self.blocks[x][y] == 2 else '#FF0000' if self.blocks[x][y] == 3 else '#00FFFF'
					sx = self.rect_width * x
					sy = self.rect_height * y
					canvas.create_rectangle(sx, sy, sx + self.rect_width, sy + self.rect_height, fill=fill)

	def reset(self):
		self.blocks = [[0 for _ in range(self.height)] for _ in range(self.width)]
		self.snake = Snake(0, 0, self.snake.use_ai)
		self.pellet = [randint(0, self.width - 1), randint(0, self.height - 1)]
