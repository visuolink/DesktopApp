import threading
import atexit
import cv2 as cv
import numpy as np
import time
from pyautogui import size, moveTo, doubleClick
from pynput.mouse import Controller, Button
from platform import system
from subprocess import call

from Visuolink.core.models.hand_detection import HandDetection
from Visuolink.core.utils import scale, get_cords, get_distance, get_angle, windowResize

# -----------------------------
# SETTINGS
# -----------------------------
ROI_X1, ROI_Y1, ROI_X2, ROI_Y2 = 200, 100, 400, 250
prev_mouse_x, prev_mouse_y = 0, 0
smooth_factor = 8
TARGET_FPS = 25
MIN_WIDTH, MIN_HEIGHT = 160, 120
MAX_WIDTH, MAX_HEIGHT = 640, 480
FRAME_SKIP = 2

# -----------------------------
# THREAD CONTROL
# -----------------------------
hand_tracking_thread = None
stop_hand_tracking = False

# -----------------------------
# VOLUME CONTROL
# -----------------------------
def setVolume(percent):
    os_name = system()
    percent = np.clip(percent, 0, 100)
    try:
        if os_name == "Windows":
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            vol_db = scale(percent, 0, 100, -63, 0)
            volume.SetMasterVolumeLevel(vol_db, None)
        elif os_name == "Linux":
            call(["amixer", "sset", "Master", f"{percent}%"])
        elif os_name == "Darwin":
            volume_mac = int(percent / 6.25)
            call(["osascript", "-e", f"set volume output volume {volume_mac}"])
        else:
            return f"❌ {os_name} not supported for volume control"
    except Exception as e:
        return f"⚠️ Volume error: {e}"
    return 0

# -----------------------------
# HAND GESTURES
# -----------------------------
def handMouseGesture(landmarks, h, w, thumb_x, thumb_y):
    global prev_mouse_x, prev_mouse_y, smooth_factor
    screen_width, screen_height = size()
    mouse = Controller()

    index_angle = get_angle([landmarks[5].x, landmarks[5].y],
                            [landmarks[6].x, landmarks[6].y],
                            [landmarks[8].x, landmarks[8].y])
    middle_angle = get_angle([landmarks[9].x, landmarks[9].y],
                             [landmarks[10].x, landmarks[10].y],
                             [landmarks[12].x, landmarks[12].y])

    index_pip_x, index_pip_y = get_cords(landmarks[5], h, w)
    index_thumb_dist = get_distance(index_pip_x, index_pip_y, thumb_x, thumb_y)

    if index_thumb_dist < 50 and index_angle > 90:
        index_x, index_y = get_cords(landmarks[8], h, w)
        target_x = scale(index_x, ROI_X1, ROI_X2, 0, screen_width)
        target_y = scale(index_y, ROI_Y1, ROI_Y2, 0, screen_height)
        cursor_x = prev_mouse_x + (target_x - prev_mouse_x) / smooth_factor
        cursor_y = prev_mouse_y + (target_y - prev_mouse_y) / smooth_factor
        moveTo(cursor_x, cursor_y, duration=0.01)
        prev_mouse_x, prev_mouse_y = cursor_x, cursor_y
    elif index_angle < 50 < index_thumb_dist and middle_angle > 90:
        mouse.click(Button.left)
    elif middle_angle < 50 < index_thumb_dist and index_angle > 90:
        mouse.click(Button.right)
    elif index_angle < 50 < index_thumb_dist and 50 < middle_angle < 90:
        doubleClick()

# -----------------------------
# HAND TRACKING LOOP
# -----------------------------
def run_hand_tracking(do_hand_tracking=True, do_volume_gesture=False):
    global stop_hand_tracking

    os_name = system()
    if os_name == "Windows":
        cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    elif os_name == "Darwin":
        cap = cv.VideoCapture(0, cv.CAP_AVFOUNDATION)
    else:
        cap = cv.VideoCapture(0, cv.CAP_V4L2)

    if not cap.isOpened():
        print("❌ Cannot access webcam.")
        return

    frame_width, frame_height = 320, 240
    cap.set(cv.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, frame_height)

    hand_detector = HandDetection()
    frame_count = 0
    last_time = time.time()

    while not stop_hand_tracking:
        success, frame = cap.read()
        if not success:
            continue

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        frame = cv.flip(frame, 1)
        h, w = frame.shape[:2]
        frame = windowResize(h, w, frame)
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hand_detector.detectedHands(rgb_frame)

        if results:
            hand = results[0]
            landmarks = hand.landmark
            thumb_x, thumb_y = get_cords(landmarks[4], h, w)
            middle_mcp_x, middle_mcp_y = get_cords(landmarks[10], h, w)
            pinky_x, pinky_y = get_cords(landmarks[20], h, w)

            if get_distance(thumb_x, thumb_y, middle_mcp_x, middle_mcp_y) < 5:
                print("🛑 Exit gesture detected.")
                break

            if do_volume_gesture:
                dist = get_distance(thumb_x, thumb_y, pinky_x, pinky_y)
                volume_level = np.clip(scale(dist, 30, 200, 0, 100), 0, 100)
                res = setVolume(volume_level)
                if isinstance(res, str):
                    print(res)
                    break

            if do_hand_tracking:
                handMouseGesture(landmarks, h, w, thumb_x, thumb_y)

        current_time = time.time()
        elapsed = current_time - last_time
        if elapsed >= 1.0:
            fps = frame_count / elapsed
            frame_count = 0
            last_time = current_time

            if fps < TARGET_FPS and frame_width > MIN_WIDTH:
                frame_width = max(frame_width // 2, MIN_WIDTH)
                frame_height = max(frame_height // 2, MIN_HEIGHT)
                cap.set(cv.CAP_PROP_FRAME_WIDTH, frame_width)
                cap.set(cv.CAP_PROP_FRAME_HEIGHT, frame_height)
            elif fps > TARGET_FPS + 5 and frame_width < MAX_WIDTH:
                frame_width = min(frame_width * 2, MAX_WIDTH)
                frame_height = min(frame_height * 2, MAX_HEIGHT)
                cap.set(cv.CAP_PROP_FRAME_WIDTH, frame_width)
                cap.set(cv.CAP_PROP_FRAME_HEIGHT, frame_height)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

# -----------------------------
# START / STOP FUNCTIONS
# -----------------------------
def start_background_hand_tracking(do_hand_tracking=True, do_volume_gesture=False):
    global hand_tracking_thread
    thread = threading.Thread(
        target=run_hand_tracking,
        args=(do_hand_tracking, do_volume_gesture),
        daemon=True
    )
    hand_tracking_thread = thread
    thread.start()

def stop_background_hand_tracking():
    global stop_hand_tracking
    stop_hand_tracking = True
    if hand_tracking_thread is not None:
        hand_tracking_thread.join()

atexit.register(stop_background_hand_tracking)
