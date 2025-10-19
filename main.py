from pico2d import *
from Background import Background


def reset_world():
    global world

    world = []

    bg = Background()
    world.append(bg)

    # 추가하기

def update_world():
    for o in world:
        o.update()

def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()

if __name__ == '__main__':
    canvas_width = 1280
    canvas_height = 720

    open_canvas(canvas_width, canvas_height)
    reset_world()

    while True:
        update_world()
        render_world()
        delay(0.01)

    close_canvas()