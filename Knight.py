from pico2d import load_image, get_time, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_z, SDLK_x
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

# 이벤트 체크 함수

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def z_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_z

def x_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_x

# 상태 클래스

class Attack:
    def __init__(self, knight):
        self.knight = knight
        self.attack_box_offset = (-51, -47, 37, 50) # 공격 히트박스 크기

    def enter(self, event):
        self.knight.frame = 0

    def exit(self):
        pass

    def do(self):
        self.knight.frame = (self.knight.frame + 1) % attack_offset[1]
        if self.knight.frame == 7:
            if self.knight.y > ground:
                next_state = self.knight.JUMP
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
            left = attack_x + l_offset
            bottom = attack_y + b_offset
            right = attack_x + r_offset
            top = attack_y + t_offset
            return (left, bottom, right, top)
        else:
            left = attack_x - r_offset
            bottom = attack_y + b_offset
            right = attack_x - l_offset
            top = attack_y + t_offset
            return (left, bottom, right, top)


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
        if total_distance == 0:
            percentage = 1.0
        else:
            percentage = traveled_distance / total_distance

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
            if self.knight.y > ground:
                next_state = self.knight.JUMP
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
        self.knight.frame = 0
        if space_down(event):
            self.knight.y_velocity = 20
        elif right_down(event) or left_up(event):
            self.knight.dir = self.knight.face_dir = 1
        elif left_down(event) or right_up(event):
            self.knight.dir = self.knight.face_dir = -1

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

            if self.knight.dir == 0:
                next_state = self.knight.IDLE
            else:
                next_state = self.knight.RUN

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
        return None

class Run:
    def __init__(self, knight):
        self.knight = knight

    def enter(self, event):
        self.knight.frame = 0
        if right_down(event) or left_up(event):
            self.knight.dir = self.knight.face_dir = 1
        elif left_down(event) or right_up(event):
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
        return None

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
        return None

class Knight:
    def __init__(self):
        self.x = canvas_width // 2 # 임시 시작 위치
        self.y = ground
        self.y_velocity = 0
        self.gravity = 0.7
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.body_box_offset = (-30, 0, 30, 100) # 히트박스 크기
        self.image = load_image('knight.png')

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = Jump(self)
        self.DASH = Dash(self)
        self.ATTACK = Attack(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    right_down: self.RUN,
                    left_down: self.RUN,
                    right_up: self.RUN,
                    left_up: self.RUN,
                    space_down: self.JUMP,
                    z_down: self.DASH,
                    x_down: self.ATTACK
                },
                self.RUN: {
                    right_down: self.IDLE,
                    left_down: self.IDLE,
                    right_up: self.IDLE,
                    left_up: self.IDLE,
                    space_down: self.JUMP,
                    z_down: self.DASH,
                    x_down: self.ATTACK
                },
                self.JUMP: {
                    right_down: self.JUMP,
                    left_down: self.JUMP,
                    right_up: self.JUMP,
                    left_up: self.JUMP,
                    z_down: self.DASH,
                    x_down: self.ATTACK
                },
                self.DASH: {
                },
                self.ATTACK: {
                }
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        attack_box = self.get_attack_box()
        if attack_box:
            draw_rectangle(*attack_box)

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