from pico2d import *
import game_framework
import title_mode
import play_mode

font = None
dim_image = None

def enter():
    global font, dim_image
    try:
        font = load_font('Lora-VariableFont_wght.ttf', 50)
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
                game_framework.quit()
            elif event.key == SDLK_SPACE:
                game_framework.change_mode(title_mode)


def draw():
    clear_canvas()
    play_mode.draw_world()
    dim_image.draw(640, 360, 1280, 720)

    if play_mode.winner == "Knight":
        src_x = 0
        src_y = 2048 - (128 * 9)  # 896

        play_mode.knight.image.clip_draw(
            src_x, src_y, 128, 128,
            640, 360,
            128, 128
        )

    elif play_mode.winner == "Hornet":
        src_x = 3
        src_y = 13086 - 953 - 216
        w, h = 184, 216

        play_mode.hornet.image.clip_draw(
            src_x, src_y, w, h,
            640, 360,
            w * 0.7, h * 0.7
        )

    if play_mode.winner:
        font.draw(490, 470, f"{play_mode.winner} WINS!", (255, 0, 0))

    font.draw(390, 250, "Press SPACE to Restart", (255, 255, 255))
    update_canvas()


def update():
    pass


def pause():
    pass


def resume():
    pass