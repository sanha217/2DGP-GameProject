from pico2d import load_image, get_time, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDL_GetKeyboardState, \
    SDLK_j, SDLK_l, SDLK_i, SDLK_SEMICOLON, SDLK_QUOTE, \
    SDL_SCANCODE_J, SDL_SCANCODE_L, SDL_SCANCODE_I

from state_machine import StateMachine

canvas_width = 1280
canvas_height = 720

# 기존 Knight용 설정 (다른 상태들이 아직 사용하므로 유지)
frame_size = 128
ground = 90
x_velocity = 5

# 오프셋 설정 (Run, Jump 등은 아직 기존 것 사용)
run_offset = [1, 9]
jump_offset = [10, 12]
dash_offset = [5, 7]
attack_offset = [4, 8]
attack_effect_offset = [13, 13]


def l_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_l


def l_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_l


def j_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_j


def j_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_j


def i_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_i


def semicolon_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SEMICOLON


def quote_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_QUOTE


class Attack:
    def __init__(self, hornet):
        self.hornet = hornet
        self.attack_box_offset = (-51, -47, 37, 50)

    def enter(self, event):
        self.hornet.frame = 0

    def exit(self):
        pass

    def do(self):
        self.hornet.frame = (self.hornet.frame + 1) % attack_offset[1]
        if self.hornet.frame == 7:
            keystate = SDL_GetKeyboardState(None)

            if self.hornet.y > ground:
                next_state = self.hornet.JUMP
            elif keystate[SDL_SCANCODE_L]:
                self.hornet.dir = 1
                self.hornet.face_dir = 1
                next_state = self.hornet.RUN
            elif keystate[SDL_SCANCODE_J]:
                self.hornet.dir = -1
                self.hornet.face_dir = -1
                next_state = self.hornet.RUN
            else:
                next_state = self.hornet.IDLE

            self.hornet.state_machine.cur_state.exit()
            self.hornet.state_machine.cur_state = next_state
            self.hornet.state_machine.cur_state.enter(('ATTACK_END', 0))

    def draw(self):
        # 아직 수정되지 않음 (Knight 기준)
        if self.hornet.face_dir == 1:
            self.hornet.image.clip_draw(
                self.hornet.frame * frame_size,
                2048 - frame_size * attack_offset[0],  # 임시로 2048 하드코딩 (기존 로직 유지)
                frame_size, frame_size,
                self.hornet.x, self.hornet.y,
                frame_size, frame_size
            )
        else:
            self.hornet.image.clip_composite_draw(
                self.hornet.frame * frame_size,
                2048 - frame_size * attack_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.hornet.x, self.hornet.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        l_offset, b_offset, r_offset, t_offset = self.attack_box_offset
        attack_x = self.hornet.x + (60 * self.hornet.face_dir)
        attack_y = self.hornet.y - 20

        if self.hornet.face_dir == 1:
            return (attack_x + l_offset, attack_y + b_offset, attack_x + r_offset, attack_y + t_offset)
        else:
            return (attack_x - r_offset, attack_y + b_offset, attack_x - l_offset, attack_y + t_offset)


class Dash:
    def __init__(self, hornet):
        self.hornet = hornet
        self.dash_distance = frame_size * 3
        self.dash_speed = 25

    def enter(self, event):
        self.hornet.frame = 0
        self.hornet.dir = self.hornet.face_dir
        self.start_x = self.hornet.x

    def exit(self):
        self.hornet.dir = 0

    def do(self):
        total_frames = dash_offset[1]
        total_distance = self.dash_distance
        traveled_distance = abs(self.hornet.x - self.start_x)

        percentage = 1.0 if total_distance == 0 else traveled_distance / total_distance
        self.hornet.frame = int(percentage * total_frames)
        if self.hornet.frame >= total_frames:
            self.hornet.frame = total_frames - 1

        self.hornet.x += self.hornet.dir * self.dash_speed
        self.hornet.x = max(frame_size // 2, min(self.hornet.x, canvas_width - frame_size // 2))

        hit_wall = False
        if self.hornet.dir == 1 and self.hornet.x == canvas_width - frame_size // 2:
            hit_wall = True
        elif self.hornet.dir == -1 and self.hornet.x == frame_size // 2:
            hit_wall = True

        traveled_distance = abs(self.hornet.x - self.start_x)

        if traveled_distance >= self.dash_distance or hit_wall:
            keystate = SDL_GetKeyboardState(None)

            if self.hornet.y > ground:
                next_state = self.hornet.JUMP
            elif keystate[SDL_SCANCODE_L]:
                self.hornet.dir = 1
                self.hornet.face_dir = 1
                next_state = self.hornet.RUN
            elif keystate[SDL_SCANCODE_J]:
                self.hornet.dir = -1
                self.hornet.face_dir = -1
                next_state = self.hornet.RUN
            else:
                next_state = self.hornet.IDLE

            self.hornet.state_machine.cur_state.exit()
            self.hornet.state_machine.cur_state = next_state
            self.hornet.state_machine.cur_state.enter(('DASH_END', 0))

    def draw(self):
        # 아직 수정되지 않음
        if self.hornet.face_dir == 1:
            self.hornet.image.clip_draw(
                self.hornet.frame * frame_size,
                2048 - frame_size * dash_offset[0],
                frame_size, frame_size,
                self.hornet.x, self.hornet.y,
                frame_size, frame_size
            )
        else:
            self.hornet.image.clip_composite_draw(
                self.hornet.frame * frame_size,
                2048 - frame_size * dash_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.hornet.x, self.hornet.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return None


class Jump:
    global y_velocity

    def __init__(self, hornet):
        self.hornet = hornet

    def enter(self, event):
        if i_down(event):
            self.hornet.frame = 0
            self.hornet.y_velocity = 20

        keystate = SDL_GetKeyboardState(None)
        if keystate[SDL_SCANCODE_L] and keystate[SDL_SCANCODE_J]:
            self.hornet.dir = 0
        elif keystate[SDL_SCANCODE_L]:
            self.hornet.dir = 1
            self.hornet.face_dir = 1
        elif keystate[SDL_SCANCODE_J]:
            self.hornet.dir = -1
            self.hornet.face_dir = -1
        else:
            self.hornet.dir = 0

    def exit(self):
        pass

    def do(self):
        max_velocity = 20.0
        min_velocity = -20.0
        velocity_range = max_velocity - min_velocity
        num_frames = jump_offset[1]
        clamped_v = self.hornet.y_velocity
        if clamped_v > max_velocity:
            clamped_v = max_velocity
        elif clamped_v < min_velocity:
            clamped_v = min_velocity
        percentage = (clamped_v - min_velocity) / velocity_range
        reversed_percentage = 1.0 - percentage
        target_frame = int(reversed_percentage * (num_frames - 1))

        self.hornet.frame = target_frame
        self.hornet.x += self.hornet.dir * x_velocity
        self.hornet.y += self.hornet.y_velocity
        self.hornet.y_velocity -= self.hornet.gravity

        if self.hornet.y <= ground:
            self.hornet.y = ground

            keystate = SDL_GetKeyboardState(None)
            if keystate[SDL_SCANCODE_L]:
                self.hornet.dir = 1
                self.hornet.face_dir = 1
                next_state = self.hornet.RUN
            elif keystate[SDL_SCANCODE_J]:
                self.hornet.dir = -1
                self.hornet.face_dir = -1
                next_state = self.hornet.RUN
            else:
                self.hornet.dir = 0
                next_state = self.hornet.IDLE

            self.hornet.state_machine.cur_state.exit()
            self.hornet.state_machine.cur_state = next_state
            self.hornet.state_machine.cur_state.enter(('LAND', 0))

    def draw(self):
        # 아직 수정되지 않음
        if self.hornet.face_dir == 1:
            self.hornet.image.clip_draw(
                self.hornet.frame * frame_size,
                2048 - frame_size * jump_offset[0],
                frame_size, frame_size,
                self.hornet.x, self.hornet.y,
                frame_size, frame_size
            )
        else:
            self.hornet.image.clip_composite_draw(
                self.hornet.frame * frame_size,
                2048 - frame_size * jump_offset[0],
                frame_size, frame_size,
                0, 'h',
                self.hornet.x, self.hornet.y,
                frame_size, frame_size
            )

    def get_attack_box(self):
        return None


class Run:
    def __init__(self, hornet):
        self.hornet = hornet
        self.width = 159
        self.height = 191
        self.start_x = 3
        self.start_y_top = 1191
        self.gap = 3
        self.frame_count = 8

        self.display_width = self.width // 1.5
        self.display_height = self.height // 1.5

    def enter(self, event):
        self.hornet.frame = 0
        if l_down(event) or j_up(event):
            self.hornet.dir = self.hornet.face_dir = 1
        elif j_down(event) or l_up(event):
            self.hornet.dir = self.hornet.face_dir = -1

    def exit(self):
        pass

    def do(self):
        self.hornet.frame = (self.hornet.frame + 1) % self.frame_count
        self.hornet.x += self.hornet.dir * x_velocity

    def draw(self):
        left = self.start_x + (self.hornet.frame * (self.width + self.gap))
        bottom = self.hornet.image_height - self.start_y_top - self.height

        if self.hornet.face_dir == 1:
            self.hornet.image.clip_composite_draw(
                left, bottom, self.width, self.height,
                0, 'h',
                self.hornet.x, self.hornet.y,
                self.display_width, self.display_height
            )
        else:
            self.hornet.image.clip_draw(
                left, bottom, self.width, self.height,
                self.hornet.x, self.hornet.y,
                self.display_width, self.display_height
            )

    def get_attack_box(self):
        return None


class Idle:
    def __init__(self, hornet):
        self.hornet = hornet
        self.width = 184
        self.height = 216
        self.start_x = 3
        self.start_y_top = 953
        self.gap = 3
        self.frame_count = 6

        self.display_width = self.width // 1.5
        self.display_height = self.height // 1.5

    def enter(self, event):
        self.hornet.frame = 0
        self.hornet.dir = 0
        self.hornet.idle_start_time = get_time()

    def exit(self):
        pass

    def do(self):
        if get_time() - self.hornet.idle_start_time >= 0.2:
            self.hornet.frame = (self.hornet.frame + 1) % self.frame_count
            self.hornet.idle_start_time = get_time()

    def draw(self):
        left = self.start_x + (self.hornet.frame * (self.width + self.gap))
        bottom = self.hornet.image_height - self.start_y_top - self.height

        if self.hornet.face_dir == 1:
            self.hornet.image.clip_composite_draw(
                left, bottom, self.width, self.height,
                0, 'h',
                self.hornet.x, self.hornet.y,
                self.display_width, self.display_height
            )
        else:
            self.hornet.image.clip_draw(
                left, bottom, self.width, self.height,
                self.hornet.x, self.hornet.y,
                self.display_width, self.display_height
            )

    def get_attack_box(self):
        return None


class Hornet:
    def __init__(self):
        self.x = canvas_width // 2
        self.y = ground + 10
        self.y_velocity = 0
        self.gravity = 0.7
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.body_box_offset = (-30, 0, 30, 100)

        self.image = load_image('hornet.png')
        self.image_width = 2392
        self.image_height = 13086

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = Jump(self)
        self.DASH = Dash(self)
        self.ATTACK = Attack(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    l_down: self.RUN,
                    j_down: self.RUN,
                    l_up: self.RUN,
                    j_up: self.RUN,
                    i_down: self.JUMP,
                    semicolon_down: self.DASH,
                    quote_down: self.ATTACK
                },
                self.RUN: {
                    l_down: self.IDLE,
                    j_down: self.IDLE,
                    l_up: self.IDLE,
                    j_up: self.IDLE,
                    i_down: self.JUMP,
                    semicolon_down: self.DASH,
                    quote_down: self.ATTACK
                },
                self.JUMP: {
                    l_down: self.JUMP,
                    j_down: self.JUMP,
                    l_up: self.JUMP,
                    j_up: self.JUMP,
                    semicolon_down: self.DASH,
                    quote_down: self.ATTACK
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