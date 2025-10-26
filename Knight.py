from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT
from state_machine import StateMachine

# 설정 변수

canvas_width = 1280
canvas_height = 720
image_size = 2048
frame_size = 128

ground = 90
x_velocity = 5
y_velocity = 5

# [y오프셋. 프레임 오프셋]
idle_offset = [9, 7]
run_offset = [1, 9]

# 이벤트 체크 함수

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

# 상태 클래스

class Jump:
    def __init__(self, knight):
        pass

    def enter(self, event):
        pass

    def exit(self):
        pass

    def do(self):
        pass

    def draw(self):
        pass

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

class Knight:
    def __init__(self):
        self.x = canvas_width // 2 # 임시 시작 위치
        self.y = ground
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.image = load_image('knight.png')

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    right_down: self.RUN,
                    left_down: self.RUN,
                    right_up: self.RUN,
                    left_up: self.RUN
                },
                self.RUN: {
                    right_down: self.IDLE,
                    left_down: self.IDLE,
                    right_up: self.IDLE,
                    left_up: self.IDLE
                },
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_state_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))