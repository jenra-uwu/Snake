from random import randint, choice


def update_coördinates(direction, x, y, width, height, undo=False):
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
			self.x, self.y = update_coördinates(self.direction, self.x, self.y, width, height)
			self.prev_dirs = [self.direction] + self.prev_dirs[:-1]
			self.kp = False

	def ai(self, world):
		body_dir = reverse(self.direction)
		dirs = [(body_dir + 1) % 4, (body_dir + 2) % 4, (body_dir + 3) % 4]
		valid_dirs = []

		for dir in dirs:
			x, y = update_coördinates(dir, self.x, self.y, world.width, world.height)
			if world.blocks[x][y] == 2:
				self.direction = dir
				return
			elif world.blocks[x][y] != 1:
				valid_dirs += [dir]
			else:
				fx, fy = update_coördinates(self.prev_dirs[-1], x, y, world.width, world.height, undo=True)
				ox, oy = update_coördinates((1+2+3) - reverse(self.prev_dirs[-1]) - self.direction - dir, x, y, world.width, world.height, undo=True)
				if world.blocks[fx][fy] != 1 and world.blocks[ox][oy] != 1:
					valid_dirs += [dir]

		if valid_dirs:
			x_dist = world.pellet[0] - self.x
			y_dist = world.pellet[1] - self.y
			if x_dist < -world.width / 2 or x_dist > world.width / 2:
				x_dist = -x_dist
			if y_dist < -world.height / 2 or y_dist > world.height / 2:
				y_dist = -y_dist
			x_dir = 0 if x_dist < 0 else 1 if x_dist else -1
			y_dir = 2 if y_dist < 0 else 3 if y_dist else -1
			if y_dir in valid_dirs:
				self.direction = y_dir
			elif x_dir in valid_dirs:
				self.direction = x_dir
			else:
				self.direction = choice(valid_dirs)
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

	def tick(self):
		self.snake.tick(self)

		self.blocks = [[0 for _ in range(self.height)] for _ in range(self.width)]
		self.blocks[self.pellet[0]][self.pellet[1]] = 2

		x = self.snake.x
		y = self.snake.y
		if self.blocks[x][y] == 2:
			self.snake.prev_dirs += self.snake.prev_dirs[-1:]
			while True:
				self.pellet = [randint(0, self.width - 1), randint(0, self.height - 1)]
				if self.blocks[self.pellet[0]][self.pellet[1]] == 0:
					break

		first = True
		for d in self.snake.prev_dirs:
			if not self.snake.moving and not self.snake.dead and first:
				self.blocks[x][y] = 4
				first = False
			elif self.blocks[x][y] == 1:
				self.blocks[x][y] = 3
				self.snake.dead = True
				self.snake.moving = False
			elif self.blocks[x][y] != 3:
				self.blocks[x][y] = 1
			x, y = update_coördinates(d, x, y, self.width, self.height, undo=True)

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
