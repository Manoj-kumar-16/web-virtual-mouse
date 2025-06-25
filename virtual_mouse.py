import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Video capture
cap = cv2.VideoCapture(0)

# Volume setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
min_vol, max_vol = volume_ctrl.GetVolumeRange()[0], volume_ctrl.GetVolumeRange()[1]

# Screen resolution
screen_w, screen_h = pyautogui.size()

# States
prev_volume, prev_brightness = -1, -1
last_cursor_move_time = time.time()
cursor_frozen = False
selected_item = None
selection_made = False
last_pinched_time = 0

def get_finger_states(hand_landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for id in range(1, 5):
        fingers.append(1 if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y else 0)

    return fingers

def is_fist(fingers): return sum(fingers) == 0
def is_five(fingers): return sum(fingers) == 5

def draw_feedback(img, text, pos=(50, 50), color=(0, 255, 0)):
    cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

def control_volume(fist_up, fist_down):
    global prev_volume
    current_vol = volume_ctrl.GetMasterVolumeLevelScalar()
    step = 0.05
    if fist_up and current_vol < 1.0:
        new_vol = min(current_vol + step, 1.0)
        volume_ctrl.SetMasterVolumeLevelScalar(new_vol, None)
        prev_volume = int(new_vol * 100)
    elif fist_down and current_vol > 0.0:
        new_vol = max(current_vol - step, 0.0)
        volume_ctrl.SetMasterVolumeLevelScalar(new_vol, None)
        prev_volume = int(new_vol * 100)
    return prev_volume

def control_brightness(up, down):
    global prev_brightness
    try:
        current = sbc.get_brightness(display=0)[0]
        step = 5
        if up:
            new = min(current + step, 100)
            sbc.set_brightness(new)
            prev_brightness = new
        elif down:
            new = max(current - step, 0)
            sbc.set_brightness(new)
            prev_brightness = new
        return prev_brightness
    except Exception:
        return -1

def get_hand_label(results, hand_no):
    return results.multi_handedness[hand_no].classification[0].label  # 'Left' or 'Right'

def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def detect_pinch(lm, w, h):
    x1, y1 = int(lm.landmark[4].x * w), int(lm.landmark[4].y * h)
    x2, y2 = int(lm.landmark[8].x * w), int(lm.landmark[8].y * h)
    return distance((x1, y1), (x2, y2)) < 40

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    current_time = time.time()

    if results.multi_hand_landmarks:
        for i, hand_lm in enumerate(results.multi_hand_landmarks):
            label = get_hand_label(results, i)
            fingers = get_finger_states(hand_lm)
            mp_draw.draw_landmarks(img, hand_lm, mp_hands.HAND_CONNECTIONS)

            if label == 'Left':
                # Volume control
                if is_fist(fingers):
                    if hand_lm.landmark[8].y < hand_lm.landmark[0].y:
                        v = control_volume(True, False)
                        draw_feedback(img, f"Volume Up: {v}%", (10, 70))
                    else:
                        v = control_volume(False, True)
                        draw_feedback(img, f"Volume Down: {v}%", (10, 70))

                # Brightness control
                elif is_five(fingers):
                    if hand_lm.landmark[8].y < hand_lm.landmark[0].y:
                        b = control_brightness(True, False)
                        draw_feedback(img, f"Brightness Up: {b}%", (10, 110))
                    else:
                        b = control_brightness(False, True)
                        draw_feedback(img, f"Brightness Down: {b}%", (10, 110))

            elif label == 'Right':
                cx, cy = int(hand_lm.landmark[8].x * w), int(hand_lm.landmark[8].y * h)
                scr_x = np.interp(cx, [0, w], [0, screen_w])
                scr_y = np.interp(cy, [0, h], [0, screen_h])
                pinch = detect_pinch(hand_lm, w, h)

                # Cursor control (1 finger)
                if fingers == [0, 1, 0, 0, 0]:
                    if not cursor_frozen:
                        pyautogui.moveTo(scr_x, scr_y)
                        last_cursor_move_time = current_time
                        draw_feedback(img, "Cursor Moving", (cx, cy))
                    elif current_time - last_cursor_move_time > 1:
                        cursor_frozen = True
                        draw_feedback(img, "Cursor Frozen", (cx, cy), (0, 0, 255))
                else:
                    if is_five(fingers):
                        cursor_frozen = False
                        draw_feedback(img, "Cursor Unfrozen", (cx, cy), (255, 0, 0))

                # Pinch to select/open when frozen
                if pinch and cursor_frozen:
                    now = time.time()
                    if now - last_pinched_time < 0.5 and selected_item:
                        pyautogui.doubleClick()
                        draw_feedback(img, "Opened", (cx, cy), (0, 0, 255))
                        selected_item = None
                        selection_made = False
                    elif not selection_made:
                        pyautogui.click()
                        selected_item = (scr_x, scr_y)
                        selection_made = True
                        draw_feedback(img, "Selected", (cx, cy), (255, 0, 0))
                    last_pinched_time = now
                else:
                    selection_made = False

                # Right click
                if fingers == [0, 1, 1, 0, 0]:
                    pyautogui.click(button='right')
                    draw_feedback(img, "Right Click", (cx, cy), (0, 255, 255))
                    time.sleep(0.3)

                # Left click
                if fingers == [0, 1, 1, 1, 0]:
                    pyautogui.click(button='left')
                    draw_feedback(img, "Left Click", (cx, cy), (255, 255, 0))
                    time.sleep(0.3)

    cv2.imshow("Gesture Control", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

