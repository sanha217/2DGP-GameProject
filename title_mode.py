from pico2d import *
import game_framework
import play_mode

image = None
font = None
controls_image = None
show_help = False


def enter():
    global image, font, controls_image, show_help
    image = load_image('title.png')

    try:
        controls_image = load_image('controls.png')
    except IOError:
        print("controls.png not found!")
        controls_image = None

    try:
        font = load_font('Lora-VariableFont_wght.ttf', 50)
    except IOError:
        font = load_font('C:/Windows/Fonts/arial.ttf', 50)

    show_help = False

def exit():
    global image, font, controls_image
    del image
    del font
    if controls_image:
        del controls_image


def handle_events():
    global show_help
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                if show_help:
                    show_help = False
                else:
                    game_framework.quit()

            elif event.key == SDLK_h:
                show_help = not show_help

            elif event.key == SDLK_SPACE:
                if not show_help:
                    game_framework.change_mode(play_mode)


def draw():
    clear_canvas()

    image.draw(640, 360, 1290, 730)

    if show_help:
        if controls_image:
            w, h = controls_image.w, controls_image.h

            new_w = w * 1.5
            new_h = h * 1.5

            controls_image.draw(640, 360, new_w, new_h)

            font.draw(350, 100, "Press H or ESC to Close", (255, 255, 255))
    else:
        font.draw(400, 100, "Press SPACE to Start", (255, 255, 255))
        font.draw(450, 50, "Press H for Help", (200, 200, 200))

    update_canvas()


def update():
    pass


def pause():
    pass


def resume():
    pass