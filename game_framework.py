# game_framework.py
import time

class GameState:
    def __init__(self, state):
        self.enter = state.enter
        self.exit = state.exit
        self.pause = state.pause
        self.resume = state.resume
        self.handle_events = state.handle_events
        self.update = state.update
        self.draw = state.draw


running = None
stack = None
frame_time = 0.0  # 프레임 시간 변수 추가


def change_mode(mode):
    global stack
    if (len(stack) > 0):
        stack[-1].exit()
        stack.pop()
    stack.append(mode)
    mode.enter()


def push_mode(mode):
    global stack
    if (len(stack) > 0):
        stack[-1].pause()
    stack.append(mode)
    mode.enter()


def pop_mode():
    global stack
    if (len(stack) > 0):
        stack[-1].exit()
        stack.pop()

    if (len(stack) > 0):
        stack[-1].resume()


def quit():
    global running
    running = False


def run(start_mode):
    global running, stack, frame_time
    running = True
    stack = [start_mode]
    start_mode.enter()

    # 시간 측정을 위한 현재 시간 초기화
    current_time = time.time()

    while running:
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()

        # 프레임 시간 계산
        frame_time = time.time() - current_time
        frame_rate = 1.0 / frame_time
        current_time += frame_time
        # print(f'Frame Time: {frame_time}, Frame Rate: {frame_rate}')

    while (len(stack) > 0):
        stack[-1].exit()
        stack.pop()