
from pico2d import *
import game_framework
import play_mode

def enter():
    global font
    try:
        font = load_font('ENCR10B.TTF', 50)
    except IOError:
        font = load_font('C:/Windows/Fonts/arial.ttf', 50)

def exit():
    pass

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_SPACE:
                game_framework.change_mode(play_mode)

def draw():
    clear_canvas()
    font.draw(400, 400, "Knight vs Hornet", (255, 255, 255))
    font.draw(350, 300, "Press SPACE to Start", (255, 255, 255))
    update_canvas()

def update():
    pass

def pause():
    pass

def resume():
    pass