from pico2d import load_image, get_time, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDL_GetKeyboardState, \
    SDLK_a, SDLK_d, SDLK_w, SDLK_f, SDLK_g, \
    SDL_SCANCODE_A, SDL_SCANCODE_D, SDL_SCANCODE_W

from state_machine import StateMachine

# 설정 변수

canvas_width = 1280
canvas_height = 720
image_size = 2048
frame_size = 128

ground = 90
x_velocity = 5

# [y오프셋. 프레임 오프셋]
idle_offset = [9, 7]
run_offset = [1, 9]
jump_offset = [10, 12]
dash_offset = [5, 7]
attack_offset = [4, 8]
attack_effect_offset = [13, 13]


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


# 상태 클래스

class Attack:
    def __init__(self, knight):
        self.knight = knight
        self.attack_box_offset = (-51, -47, 37, 50)

    def enter(self, event):
        self.knight.frame = 0

    def exit(self):
        pass

    def do(self):
        self.knight.frame = (self.knight.frame + 1) % attack_offset[1]
        if self.knight.frame == 7:
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
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
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
                self.knight.frame * frame_size,
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
        self.dash_speed = 25

    def enter(self, event):
        self.knight.frame = 0
        self.knight.dir = self.knight.face_dir
        self.start_x = self.knight.x

    def exit(self):
        self.knight.dir = 0

    def do(self):
        total_frames = dash_offset[1]
        total_distance = self.dash_distance
        traveled_distance = abs(self.knight.x - self.start_x)

        percentage = 1.0 if total_distance == 0 else traveled_distance / total_distance
        self.knight.frame = int(percentage * total_frames)
        if self.knight.frame >= total_frames:
            self.knight.frame = total_frames - 1

        self.knight.x += self.knight.dir * self.dash_speed
        self.knight.x = max(frame_size // 2, min(self.knight.x, canvas_width - frame_size // 2))

        hit_wall = False
        if self.knight.dir == 1 and self.knight.x == canvas_width - frame_size // 2:
            hit_wall = True
        elif self.knight.dir == -1 and self.knight.x == frame_size // 2:
            hit_wall = True

        traveled_distance = abs(self.knight.x - self.start_x)

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
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * dash_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * dash_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return None


class Jump:
    global y_velocity

    def __init__(self, knight):
        self.knight = knight

    def enter(self, event):
        if w_down(event):
            self.knight.frame = 0
            self.knight.y_velocity = 20

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
        max_velocity = 20.0
        min_velocity = -20.0
        velocity_range = max_velocity - min_velocity
        num_frames = jump_offset[1]
        clamped_v = self.knight.y_velocity
        if clamped_v > max_velocity:
            clamped_v = max_velocity
        elif clamped_v < min_velocity:
            clamped_v = min_velocity
        percentage = (clamped_v - min_velocity) / velocity_range
        reversed_percentage = 1.0 - percentage
        target_frame = int(reversed_percentage * (num_frames - 1))

        self.knight.frame = target_frame
        self.knight.x += self.knight.dir * x_velocity
        self.knight.y += self.knight.y_velocity
        self.knight.y_velocity -= self.knight.gravity

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
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * jump_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * jump_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return self.knight.get_body_box()

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
        self.knight.frame = (self.knight.frame + 1) % run_offset[1]
        self.knight.x += self.knight.dir * x_velocity

    def draw(self):
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * run_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * run_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return self.knight.get_body_box()


class Idle:
    def __init__(self, knight):
        self.knight = knight

    def enter(self, event):
        self.knight.frame = 0
        self.knight.dir = 0
        self.knight.idle_start_time = get_time()

    def exit(self):
        pass

    def do(self):
        if get_time() - self.knight.idle_start_time >= 0.2:
            self.knight.frame = (self.knight.frame + 1) % idle_offset[1]
            self.knight.idle_start_time = get_time()

    def draw(self):
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * idle_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )
        else:
            self.knight.image.clip_composite_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * idle_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.knight.x, self.knight.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return self.knight.get_body_box()


class Knight:
    def __init__(self):
        self.x = canvas_width // 2
        self.y = ground
        self.y_velocity = 0
        self.gravity = 0.7
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.body_box_offset = (-27, -57, 29, 58)
        self.image = load_image('knight.png')

        self.hp = 5
        self.hp_image = load_image('hp.png')

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = Jump(self)
        self.DASH = Dash(self)
        self.ATTACK = Attack(self)
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
                    g_down: self.ATTACK
                },
                self.RUN: {
                    d_down: self.IDLE,
                    a_down: self.IDLE,
                    d_up: self.IDLE,
                    a_up: self.IDLE,
                    w_down: self.JUMP,
                    f_down: self.DASH,
                    g_down: self.ATTACK
                },
                self.JUMP: {
                    d_down: self.JUMP,
                    a_down: self.JUMP,
                    d_up: self.JUMP,
                    a_up: self.JUMP,
                    f_down: self.DASH,
                    g_down: self.ATTACK
                },
                self.DASH: {
                },
                self.ATTACK: {
                }
            }
        )

    def update(self):
        self.state_machine.update()

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