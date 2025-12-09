# game_world.py

objects = [[], [], []]

collision_pairs = {}


def add_object(o, depth=0):
    objects[depth].append(o)

def add_objects(ol, depth=0):
    objects[depth] += ol

def update():
    for layer in objects:
        for o in layer:
            o.update()

def render():
    for layer in objects:
        for o in layer:
            o.draw()

def remove_collision_object(o):
    for pairs in collision_pairs.values():
        if o in pairs[0]:
            pairs[0].remove(o)
        if o in pairs[1]:
            pairs[1].remove(o)

def remove_object(o):
    for layer in objects:
        if o in layer:
            layer.remove(o)
            remove_collision_object(o)
            del o
            return
    raise ValueError('Cannot delete non existing object')

def clear():
    for layer in objects:
        layer.clear()
    collision_pairs.clear()

# 충돌처리

def add_collision_pair(group, a, b):
    if group not in collision_pairs:
        print(f'Added new group {group}')
        collision_pairs[group] = [[], []]
    if a:
        collision_pairs[group][0].append(a)
    if b:
        collision_pairs[group][1].append(b)

def collide(a, b):
    # 1. a와 b의 몸통 충돌 확인
    left_a, bottom_a, right_a, top_a = a.get_body_box()
    left_b, bottom_b, right_b, top_b = b.get_body_box()

    if not (left_a > right_b or right_a < left_b or top_a < bottom_b or bottom_a > top_b):
        return True

    # 2. a가 공격 중이라면, a의 공격 박스(Attack Box)와 b의 몸통 충돌 확인
    if hasattr(a, 'get_attack_box') and a.get_attack_box():
        left_a, bottom_a, right_a, top_a = a.get_attack_box()
        if not (left_a > right_b or right_a < left_b or top_a < bottom_b or bottom_a > top_b):
            return True

    # 3. b가 공격 중이라면, b의 공격 박스(Attack Box)와 a의 몸통 충돌 확인
    if hasattr(b, 'get_attack_box') and b.get_attack_box():
        left_b, bottom_b, right_b, top_b = b.get_attack_box()
        left_a, bottom_a, right_a, top_a = a.get_body_box()
        if not (left_b > right_a or right_b < left_a or top_b < bottom_a or bottom_b > top_a):
            return True

    return False

def handle_collisions():
    for group, pairs in collision_pairs.items():
        for a in pairs[0]:
            for b in pairs[1]:
                if collide(a, b):
                    a.handle_collision(group, b)
                    b.handle_collision(group, a)