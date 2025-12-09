from pico2d import load_image, get_time, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDL_GetKeyboardState, \
    SDLK_a, SDLK_d, SDLK_w, SDLK_f, SDLK_g, SDLK_t, \
    SDL_SCANCODE_A, SDL_SCANCODE_D, SDL_SCANCODE_W

from state_machine import StateMachine
from pico2d import load_image, get_time, draw_rectangle, load_wav
import game_framework
import game_world

# 설정 변수

canvas_width = 1280
canvas_height = 720
image_size = 2048
frame_size = 128

ground = 90

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 60.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

TIME_PER_ATTACK = 0.15
ATTACK_PER_TIME = 1.0 / TIME_PER_ATTACK

TIME_PER_SKILL = 0.5
SKILL_PER_TIME = 1.0 / TIME_PER_SKILL

# [y오프셋. 프레임 오프셋]
idle_offset = [9, 7]
run_offset = [1, 9]
jump_offset = [10, 12]
dash_offset = [5, 7]
attack_offset = [4, 8]
attack_effect_offset = [13, 13]
skill_offset = [11, 16]

# 이벤트 체크 함수 (키 변경 적용: A, D, W, F, G)

def d_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d


def d_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d


def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a


def w_down(e):  # 점프
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_w


def f_down(e):  # 대시
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_f


def g_down(e):  # 공격
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_g

def t_down(e): # 스킬
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_t

# 투사체 클래스
class KnightSkill:
    image = None

    def __init__(self, knight, x, y, dir):
        if KnightSkill.image == None:
            KnightSkill.image = load_image('knight skill.png')
        self.knight = knight
        self.x, self.y, self.dir = x, y, dir
        self.speed = RUN_SPEED_PPS * 2.0
        self.frame = 0
        self.hit_objects = []

    def update(self):
        self.x += self.dir * self.speed * game_framework.frame_time
        self.frame = (self.frame + 3 * ACTION_PER_TIME * game_framework.frame_time) % 3

        if self.x < -100 or self.x > canvas_width + 100:
            game_world.remove_object(self)
            if self in self.knight.projectiles:
                self.knight.projectiles.remove(self)

    def draw(self):
        frame_idx = int(self.frame)
        bottom = (2 - frame_idx) * 128

        if self.dir == 1:
            self.image.clip_draw(0, bottom, 512, 128, self.x, self.y)
        else:
            self.image.clip_composite_draw(0, bottom, 512, 128, 0, 'h', self.x, self.y, 512, 128)

        draw_rectangle(*self.get_body_box())

    def get_body_box(self):
        return self.x - 256, self.y - 64, self.x + 256, self.y + 64

    def handle_collision(self, group, other):
        if group == 'knight_skill:hornet':
            if other in self.hit_objects:
                return

            other.hp -= 1
            print(f"Skill Hit! Hornet HP: {other.hp}")

            self.hit_objects.append(other)


# 상태 클래스

class Skill:
    def __init__(self, knight):
        self.knight = knight
        self.has_fired = False

    def enter(self, event):
        self.knight.frame = 0
        self.has_fired = False

    def exit(self):
        pass

    def do(self):
        total_frames = skill_offset[1]
        self.knight.frame += total_frames * SKILL_PER_TIME * game_framework.frame_time

        if not self.has_fired and int(self.knight.frame) >= 8:
            skill = KnightSkill(self.knight, self.knight.x, self.knight.y, self.knight.face_dir)
            game_world.add_object(skill, 1)
            self.knight.projectiles.append(skill)
            game_world.add_collision_pair('knight_skill:hornet', skill, None)
            self.has_fired = True

        if int(self.knight.frame) >= total_frames:
            self.knight.frame = total_frames - 1

            if self.knight.y > ground:
                self.knight.state_machine.cur_state = self.knight.JUMP
            else:
                self.knight.state_machine.cur_state = self.knight.IDLE

            self.knight.state_machine.cur_state.enter(('SKILL_END', 0))

    def draw(self):
        cur_frame = int(self.knight.frame)
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                cur_frame * frame_size,
                image_size - frame_size * skill_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                cur_frame * frame_size,
                image_size - frame_size * skill_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )

    def get_body_box(self):
        return self.knight.get_body_box()

    def get_attack_box(self):
        return None

class Attack:
    def __init__(self, knight):
        self.knight = knight
        self.attack_box_offset = (-51, -47, 37, 50)
        self.attack_sound = load_wav('Sword Sound.mp3')
        self.attack_sound.set_volume(32)

    def enter(self, event):
        self.knight.frame = 0
        self.has_attacked = False
        self.attack_sound.play()

    def exit(self):
        pass

    def do(self):
        total_frames = attack_offset[1]
        self.knight.frame = (self.knight.frame + total_frames * ATTACK_PER_TIME * game_framework.frame_time) % total_frames

        if int(self.knight.frame) == total_frames - 1:
            keystate = SDL_GetKeyboardState(None)

            if self.knight.y > ground:
                next_state = self.knight.JUMP
            elif keystate[SDL_SCANCODE_D]:
                self.knight.dir = 1
                self.knight.face_dir = 1
                next_state = self.knight.RUN
            elif keystate[SDL_SCANCODE_A]:
                self.knight.dir = -1
                self.knight.face_dir = -1
                next_state = self.knight.RUN
            else:
                next_state = self.knight.IDLE

            self.knight.state_machine.cur_state.exit()
            self.knight.state_machine.cur_state = next_state
            self.knight.state_machine.cur_state.enter(('ATTACK_END', 0))

    def draw(self):
        cur_frame = int(self.knight.frame)  # 실수형 프레임을 정수로 변환
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                cur_frame * frame_size,
                image_size - frame_size * attack_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
            self.knight.image.clip_composite_draw(
                attack_effect_offset[1] * frame_size,
                image_size - frame_size * attack_effect_offset[0],
                frame_size, frame_size,
                0, 'v',
                self.knight.x + (60 * self.knight.face_dir), self.knight.y - 20,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                cur_frame * frame_size,
                image_size - frame_size * attack_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
            self.knight.image.clip_composite_draw(
                attack_effect_offset[1] * frame_size,
                image_size - frame_size * attack_effect_offset[0],
                frame_size, frame_size,
                0, 'vh',
                self.knight.x + (60 * self.knight.face_dir), self.knight.y - 20,
                frame_size, frame_size
            )

    def get_attack_box(self):
        l_offset, b_offset, r_offset, t_offset = self.attack_box_offset
        attack_x = self.knight.x + (60 * self.knight.face_dir)
        attack_y = self.knight.y - 20

        if self.knight.face_dir == 1:
            return (attack_x + l_offset, attack_y + b_offset, attack_x + r_offset, attack_y + t_offset)
        else:
            return (attack_x - r_offset, attack_y + b_offset, attack_x - l_offset, attack_y + t_offset)


class Dash:
    def __init__(self, knight):
        self.knight = knight
        self.dash_distance = frame_size * 3
        self.dash_speed_pps = RUN_SPEED_PPS * 3
        self.dash_sound = load_wav('Hero Dash.mp3')
        self.dash_sound.set_volume(32)

    def enter(self, event):
        self.knight.frame = 0
        self.knight.dir = self.knight.face_dir
        self.start_x = self.knight.x
        self.dash_sound.play()

    def exit(self):
        self.knight.dir = 0

    def do(self):
        total_frames = dash_offset[1]

        # 시간 기반 이동 적용
        move_dist = self.knight.dir * self.dash_speed_pps * game_framework.frame_time
        self.knight.x += move_dist
        self.knight.x = max(frame_size // 2, min(self.knight.x, canvas_width - frame_size // 2))

        traveled_distance = abs(self.knight.x - self.start_x)
        percentage = 1.0 if self.dash_distance == 0 else traveled_distance / self.dash_distance
        self.knight.frame = percentage * total_frames

        if self.knight.frame >= total_frames:
            self.knight.frame = total_frames - 1

        hit_wall = False
        if self.knight.dir == 1 and self.knight.x == canvas_width - frame_size // 2:
            hit_wall = True
        elif self.knight.dir == -1 and self.knight.x == frame_size // 2:
            hit_wall = True

        if traveled_distance >= self.dash_distance or hit_wall:
            keystate = SDL_GetKeyboardState(None)

            if self.knight.y > ground:
                next_state = self.knight.JUMP
            elif keystate[SDL_SCANCODE_D]:
                self.knight.dir = 1
                self.knight.face_dir = 1
                next_state = self.knight.RUN
            elif keystate[SDL_SCANCODE_A]:
                self.knight.dir = -1
                self.knight.face_dir = -1
                next_state = self.knight.RUN
            else:
                next_state = self.knight.IDLE

            self.knight.state_machine.cur_state.exit()
            self.knight.state_machine.cur_state = next_state
            self.knight.state_machine.cur_state.enter(('DASH_END', 0))

    def draw(self):
        cur_frame = int(self.knight.frame)
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                cur_frame * frame_size,
                image_size - frame_size * dash_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                cur_frame * frame_size,
                image_size - frame_size * dash_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return None


class Jump:
    def __init__(self, knight):
        self.knight = knight

    def enter(self, event):
        if w_down(event):
            self.knight.frame = 0
            self.knight.y_velocity = 20  # 초기 점프력 (보정 필요 가능)

        keystate = SDL_GetKeyboardState(None)
        if keystate[SDL_SCANCODE_D] and keystate[SDL_SCANCODE_A]:
            self.knight.dir = 0
        elif keystate[SDL_SCANCODE_D]:
            self.knight.dir = 1
            self.knight.face_dir = 1
        elif keystate[SDL_SCANCODE_A]:
            self.knight.dir = -1
            self.knight.face_dir = -1
        else:
            self.knight.dir = 0

    def exit(self):
        pass

    def do(self):
        # 점프 애니메이션 처리
        max_velocity = 20.0
        min_velocity = -20.0
        velocity_range = max_velocity - min_velocity
        num_frames = jump_offset[1]
        clamped_v = max(min(self.knight.y_velocity, max_velocity), min_velocity)

        percentage = (clamped_v - min_velocity) / velocity_range
        reversed_percentage = 1.0 - percentage
        target_frame = int(reversed_percentage * (num_frames - 1))
        self.knight.frame = target_frame

        # 이동 처리 (시간 기반)
        # X축 이동
        self.knight.x += self.knight.dir * RUN_SPEED_PPS * game_framework.frame_time

        # Y축 이동 (프레임 타임 적용 보정)
        time_scale = game_framework.frame_time * 60

        self.knight.y += self.knight.y_velocity * time_scale
        self.knight.y_velocity -= self.knight.gravity * time_scale

        if self.knight.y <= ground:
            self.knight.y = ground

            keystate = SDL_GetKeyboardState(None)
            if keystate[SDL_SCANCODE_D]:
                self.knight.dir = 1
                self.knight.face_dir = 1
                next_state = self.knight.RUN
            elif keystate[SDL_SCANCODE_A]:
                self.knight.dir = -1
                self.knight.face_dir = -1
                next_state = self.knight.RUN
            else:
                self.knight.dir = 0
                next_state = self.knight.IDLE

            self.knight.state_machine.cur_state.exit()
            self.knight.state_machine.cur_state = next_state
            self.knight.state_machine.cur_state.enter(('LAND', 0))

    def draw(self):
        cur_frame = int(self.knight.frame)
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                cur_frame * frame_size,
                image_size - frame_size * jump_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                cur_frame * frame_size,
                image_size - frame_size * jump_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return None


class Run:
    def __init__(self, knight):
        self.knight = knight

    def enter(self, event):
        self.knight.frame = 0
        if d_down(event) or a_up(event):
            self.knight.dir = self.knight.face_dir = 1
        elif a_down(event) or d_up(event):
            self.knight.dir = self.knight.face_dir = -1

    def exit(self):
        pass

    def do(self):
        self.knight.frame = (self.knight.frame + run_offset[1] * ACTION_PER_TIME * game_framework.frame_time) % \
                            run_offset[1]
        self.knight.x += self.knight.dir * RUN_SPEED_PPS * game_framework.frame_time

        self.knight.x = max(frame_size // 2, min(self.knight.x, canvas_width - frame_size // 2))

    def draw(self):
        cur_frame = int(self.knight.frame)
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                cur_frame * frame_size,
                image_size - frame_size * run_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                cur_frame * frame_size,
                image_size - frame_size * run_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return None


class Idle:
    def __init__(self, knight):
        self.knight = knight

    def enter(self, event):
        self.knight.frame = 0
        self.knight.dir = 0

    def exit(self):
        pass

    def do(self):
        self.knight.frame = (self.knight.frame + idle_offset[1] * ACTION_PER_TIME * game_framework.frame_time) % \
                            idle_offset[1]

    def draw(self):
        cur_frame = int(self.knight.frame)
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                cur_frame * frame_size,
                image_size - frame_size * idle_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                cur_frame * frame_size,
                image_size - frame_size * idle_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return None


class Knight:
    def __init__(self):
        self.x = canvas_width // 2
        self.y = ground
        self.y_velocity = 0
        self.gravity = 0.7
        self.frame = 0.0
        self.dir = 0
        self.face_dir = 1
        self.body_box_offset = (-27, -57, 29, 58)
        self.image = load_image('knight.png')
        self.projectiles = []

        self.hp = 5
        self.hp_image = load_image('hp.png')

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = Jump(self)
        self.DASH = Dash(self)
        self.ATTACK = Attack(self)
        self.SKILL = Skill(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    d_down: self.RUN,
                    a_down: self.RUN,
                    d_up: self.RUN,
                    a_up: self.RUN,
                    w_down: self.JUMP,
                    f_down: self.DASH,
                    g_down: self.ATTACK,
                    t_down: self.SKILL
                },
                self.RUN: {
                    d_down: self.IDLE,
                    a_down: self.IDLE,
                    d_up: self.IDLE,
                    a_up: self.IDLE,
                    w_down: self.JUMP,
                    f_down: self.DASH,
                    g_down: self.ATTACK,
                    t_down: self.SKILL
                },
                self.JUMP: {
                    d_down: self.JUMP,
                    a_down: self.JUMP,
                    d_up: self.JUMP,
                    a_up: self.JUMP,
                    f_down: self.DASH,
                    g_down: self.ATTACK,
                    t_down: self.SKILL
                },
                self.DASH: {
                },
                self.ATTACK: {
                },
                self.SKILL: {
                }
            }
        )

    def update(self):
        self.state_machine.update()
        self.x = max(frame_size // 2, min(self.x, canvas_width - frame_size // 2))

    def draw_hp(self):
        hp_width = 30
        hp_height = 40

        spacing = 45

        for i in range(self.hp):
            self.hp_image.draw(
                50 + i * spacing,
                canvas_height - 50,
                hp_width,
                hp_height
            )

    def draw(self):
        self.state_machine.draw()
        body_box = self.get_body_box()
        if body_box:
            draw_rectangle(*body_box)
        attack_box = self.get_attack_box()
        if attack_box:
            draw_rectangle(*attack_box)
        self.draw_hp()

    def handle_state_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def get_body_box(self):
        l = self.x + self.body_box_offset[0]
        b = self.y + self.body_box_offset[1]
        r = self.x + self.body_box_offset[2]
        t = self.y + self.body_box_offset[3]
        return (l, b, r, t)

    def get_attack_box(self):
        if hasattr(self.state_machine.cur_state, 'get_attack_box'):
            return self.state_machine.cur_state.get_attack_box()
        return None

    def handle_collision(self, group, other):
        if group == 'knight:hornet':
            if self.state_machine.cur_state == self.ATTACK:
                if not self.state_machine.cur_state.has_attacked:
                    if self.collide_attack_box(other):
                        other.hp -= 1
                        print(f"Hornet Hit! HP: {other.hp}")
                        self.state_machine.cur_state.has_attacked = True
            return

        if group == 'hornet:knight':
            pass

    def collide_attack_box(self, other):
        attack_box = self.get_attack_box()
        if not attack_box: return False

        body_box = other.get_body_box()

        left_a, bottom_a, right_a, top_a = attack_box
        left_b, bottom_b, right_b, top_b = body_box

        if left_a > right_b: return False
        if right_a < left_b: return False
        if top_a < bottom_b: return False
        if bottom_a > top_b: return False
        return True