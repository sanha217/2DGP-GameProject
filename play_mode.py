# play_mode.py
from pico2d import *
import game_framework
import game_world
import pause_mode
import game_over_mode

from Background import Background
from Knight import Knight
from Hornet import Hornet

# 전역 변수
boy = None
knight = None
hornet = None
winner = None
bgm = None

def enter():
    global knight, hornet, winner, bgm

    # 게임 시작 시 초기화
    game_world.clear()
    winner = None

    bgm = load_music('background.mp3')
    bgm.set_volume(12)
    bgm.repeat_play()

    bg = Background()
    game_world.add_object(bg, 0)

    knight = Knight()
    game_world.add_object(knight, 1)

    hornet = Hornet()
    game_world.add_object(hornet, 1)

    game_world.add_collision_pair('knight:hornet', knight, hornet)
    game_world.add_collision_pair('hornet:knight', hornet, knight)

    game_world.add_collision_pair('knight_skill:hornet', None, hornet)
    game_world.add_collision_pair('hornet_skill:knight', hornet, knight)


def exit():
    global bgm
    game_world.clear()

    if bgm:
        bgm.stop()
    del bgm

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.push_mode(pause_mode)

        # 각 캐릭터에게 이벤트 전달
        knight.handle_state_event(event)
        hornet.handle_state_event(event)


def update():
    global winner
    game_world.update()
    game_world.handle_collisions()

    # 게임 종료 조건 체크
    if knight.hp <= 0:
        winner = "Hornet"
        game_framework.push_mode(game_over_mode)
    elif hornet.hp <= 0:
        winner = "Knight"
        game_framework.push_mode(game_over_mode)


def draw():
    clear_canvas()
    draw_world()
    update_canvas()


def draw_world():
    game_world.render()


def pause():
    pass


def resume():
    pass