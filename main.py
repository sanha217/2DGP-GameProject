from pico2d import *
import game_world
from Background import Background
from Knight import Knight
from Hornet import Hornet

def handle_events():
    global playing

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            playing = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            playing = False
        else:
            knight.handle_state_event(event)
            hornet.handle_state_event(event)

def reset_world():
    global knight
    global hornet

    game_world.clear()

    bg = Background()
    game_world.add_object(bg, 0)

    knight = Knight()
    game_world.add_object(knight, 1)

    hornet = Hornet()
    game_world.add_object(hornet, 1)

    game_world.add_collision_pair('knight:hornet', knight, hornet)

def update_world():
    game_world.update()
    game_world.handle_collisions()

def render_world():
    clear_canvas()
    game_world.render()
    update_canvas()

if __name__ == '__main__':

    playing = True

    canvas_width = 1280
    canvas_height = 720

    open_canvas(canvas_width, canvas_height)
    reset_world()

    while playing:
        handle_events()
        update_world()
        render_world()
        delay(0.01)

    close_canvas()