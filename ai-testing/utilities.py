import math

def compute_vertical_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = math.degrees(math.atan2(dy, dx))
    return angle

def compute_length(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
