import numpy as np
import os, sys

def get_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def get_cords(landmarks: list, h, w):
    return int(landmarks.x * w), int(landmarks.y * h)


def get_angle(a, b, c):
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    return np.abs(np.degrees(radians))


def scale(length, in_min, in_max, out_min, out_max):
    length = round(max(min(length, in_max), in_min), 3)
    return int(np.interp(length, [in_min, in_max], [out_min, out_max]))


def windowResize(h, w, img):
    min_dim = min(h, w)
    start_x = (w - min_dim) // 2
    start_y = (h - min_dim) // 2
    return img[start_y:start_y + min_dim, start_x:start_x + min_dim]


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
