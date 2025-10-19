from pico2d import *
from Background import Background
from Knight import Knight

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

def reset_world():
    global world
    global knight

    world = []

    bg = Background()
    world.append(bg)

    knight = Knight()
    world.append(knight)
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