import math

def compute_vertical_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = math.degrees(math.atan2(dy, dx))
    vertical_angle = abs(90 - abs(angle))  # bližje 0 pomeni glava dol
    return vertical_angle

def is_head_dropped(angle, threshold=25):
    return angle > threshold