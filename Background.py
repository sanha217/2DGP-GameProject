from pico2d import load_image

canvas_width = 1280
canvas_height = 720

class Background:
    def __init__(self):
        self.image = load_image('BG.png')

    def draw(self):
        self.image.draw(canvas_width // 2, canvas_height // 2, canvas_width, canvas_height)

    def update(self):
        pass

