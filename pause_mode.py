from pico2d import *
import game_framework
import play_mode

font = None
dim_image = None

def enter():
    global font, dim_image
    try:
        font = load_font('ENCR10B.TTF', 50)
    except IOError:
        font = load_font('C:/Windows/Fonts/arial.ttf', 50)

    dim_image = load_image('black.png')
    dim_image.opacify(0.5)

def exit():
    global font, dim_image
    del font
    del dim_image

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.pop_mode()

def draw():
    clear_canvas()
    play_mode.draw_world()
    dim_image.draw(640, 360, 1280, 720)
    font.draw(550, 360, "PAUSED", (255, 255, 0))
    font.draw(400, 300, "Press ESC to Resume", (255, 255, 255))
    update_canvas()

def update():
    pass

def pause():
    pass

def resume():
    pass