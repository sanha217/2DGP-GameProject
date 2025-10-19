from pico2d import load_image, get_time

from state_machine import StateMachine

canvas_width = 1280
canvas_height = 720
image_size = 2048
frame_size = 128

# [y오프셋. 프레임 오프셋]
idle_offset = [9, 7]
run_offset = [17, 9]

speed = 5

class Run:
    def __init__(self, knight):
        self.knight = knight

    def enter(self, event):
        if right_down(e) or left_up(e):
            self.knight.dir = self.knight.face_dir = 1
        elif left_down(e) or right_up(e):
            self.knight.dir = self.knight.face_dir = -1

    def exit(self):
        pass

    def do(self):
        self.knight.frame = (self.knight.frame + 1) % run_offset[1]
        self.knight.x += self.knight.dir * speed

    def draw(self):
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * run_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y
            )
        else:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * run_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                flip = 'h'
            )

class Idle:
    def __init__(self, knight):
        self.knight = knight

    def enter(self, event):
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
                self.knight.x, self.knight.y
            )
        else:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * idle_offset[0],
                frame_size, frame_size,
                self.knight.x, self.knight.y,
                flip = 'h'
            )


class Knight:
    def __init__(self):
        self.x = canvas_width // 2 # 임시 시작 위치
        self.y = 90
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
                    None: self.IDLE
                }
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_state_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))