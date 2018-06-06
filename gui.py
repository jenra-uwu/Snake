from tkinter import *
from game import *

class Game(Canvas):
	def __init__(self, parent, width, height, blwidth, blheight, use_ai, *args, **kwargs):
		super().__init__(parent, width=width, height=height, *args, **kwargs)
		self.world = World(width, height, blwidth, blheight, use_ai)
		self.message = False
		self.use_ai = use_ai
		self.delay = 0 if use_ai else 100
		self.step()
		self.parent = parent
		self.parent.bind_all('<KeyPress>', self.key_down)

	def reset(self):
		self.world.reset()
		self.message = False
		self.use_ai = self.world.snake.use_ai

	def key_down(self, event):
		if event.keysym == 'p':
			self.world.snake.moving = False
			return
		if '0' <= event.keysym <= '9':
			self.delay = 12 * int(event.keysym)
		if event.keysym == 'a':
			self.use_ai = self.world.snake.use_ai = True
		self.world.snake.key_down(event)

	def tick(self):
		self.world.tick()
		if self.world.snake.dead:
			if not self.message:
				if self.use_ai:
					print('The AI died. >.<\nScore: %i' % len(self.world.snake.prev_dirs))
				else:
					print('You died! ;-;\nScore: %i' % len(self.world.snake.prev_dirs))
				self.message = True
				self.after(1000 if self.world.snake.use_ai else 5000, self.reset)

	def render(self):
		self.delete("all")
		self.world.render(self)
		self.update()

	def step(self):
		self.tick()
		self.render()
		self.after(self.delay, self.step)

def main():
	use_ai = False

	width = 1000
	height = 750

	root = Tk()
	root.geometry('%ix%i' % (width, height))
	root.resizable(width = False, height = False)

	canvas = Game(root, width, height, 20, 20, use_ai, bg='#000000')
	canvas.pack(fill=BOTH)

	root.lift()
	root.wm_attributes('-topmost', True)
	root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
	root.focus_set()
	root.mainloop()

if __name__ == '__main__':
	main()

