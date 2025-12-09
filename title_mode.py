from pico2d import *
import game_framework
import play_mode

image = None
font = None


def enter():
    global image, font
    image = load_image('title.png')
    try:
        font = load_font('ENCR10B.TTF', 50)
    except IOError:
        font = load_font('C:/Windows/Fonts/arial.ttf', 50)


def exit():
    global image, font
    del image
    del font


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

    image.draw(640, 360, 1280, 720)

    font.draw(400, 100, "Press SPACE to Start", (255, 255, 255))
    update_canvas()


def update():
    pass


def pause():
    pass


def resume():
    pass