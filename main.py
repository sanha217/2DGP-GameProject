# main.py
from pico2d import *
import game_framework
import title_mode

canvas_width = 1280
canvas_height = 720

open_canvas(canvas_width, canvas_height)
game_framework.run(title_mode)
close_canvas()