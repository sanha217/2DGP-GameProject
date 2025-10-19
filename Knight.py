from pico2d import load_image

from state_machine import StateMachine

canvas_width = 1280
canvas_height = 720
image_size = 2048
frame_size = 128

idle_y_offset = 8
run_y_offset = 16

class Idle:
    def __init__(self, knight):
        self.knight = knight

    def enter(self):
        self.knight.dir = 0

    def exit(self):
        pass

    def do(self):
        self.knight.frame = (self.knight.frame + 1) % 7

    def draw(self):
        if self.knight.face_dir == 1:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * idle_y_offset,
                frame_size, frame_size,
                self.knight.x, self.knight.y
            )
        else:
            self.knight.image.clip_draw(
                self.knight.frame * frame_size,
                image_size - frame_size * idle_y_offset,
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
        self.state_machine = StateMachine(
        )

    def update(self):
        pass

    def draw(self):
        pass

    def handle_state_event(self, state):
        pass