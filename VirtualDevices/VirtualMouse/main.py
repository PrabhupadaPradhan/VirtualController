import cv2
import mediapipe as mp
import pyautogui as py
from google.protobuf.json_format import MessageToDict
from math import sqrt
cap = cv2.VideoCapture(0)
hand_detector = mp.solutions.hands.Hands()
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = py.size()
thumb_x = 0
thumb_y = 0
index_x = 0
index_y = 0
middle_x = 0
middle_y = 0
ring_x = 0
ring_y = 0
ratio = 2
py.FAILSAFE = False
def dis(x1, y1, x2, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks
    if hands:
        if output.multi_handedness:
            for hand_label in output.multi_handedness:
                hand_type = hand_label.classification[0].label
        for hand in hands:
            drawing_utils.draw_landmarks(frame, hand)
            landmarks = hand.landmark
            for id, landmark in enumerate(landmarks):
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)
                print(landmark.z)
                if id == 8:
                    cv2.circle(img = frame, center = (x, y), radius = 30, color = (0, 255, 255))
                    index_x = screen_width / frame_width * x * ratio
                    index_y = screen_height / frame_height * y * ratio
                    if dis(thumb_x, thumb_y, index_x, index_y) < 120:
                        py.click()
                        print("click")
                        py.sleep(1)
                if id == 4:
                    cv2.circle(img = frame, center = (x, y), radius = 30, color = (0, 255, 255))
                    thumb_x = screen_width / frame_width * x * ratio
                    thumb_y = screen_height / frame_height * y * ratio
                    py.moveTo(thumb_x, thumb_y)
                if id == 12:
                    cv2.circle(img = frame, center = (x, y), radius = 30, color = (0, 255, 255))
                    middle_x = screen_width / frame_width * x * ratio
                    middle_y = screen_height / frame_height * y * ratio
                    if len(hands) == 1 and dis(ring_x, ring_y, middle_x, middle_y) < 120:
                        if hand_type == "Left":
                            print("Scroll-up")
                            py.scroll(100)
                        elif hand_type == "Right":
                            print("Scroll-down")
                            py.scroll(-100)
                if id == 16:
                    cv2.circle(img = frame, center = (x, y), radius = 30, color = (0, 255, 255))
                    ring_x = screen_width / frame_width * x * ratio
                    ring_y = screen_height / frame_height * y * ratio
    cv2.imshow("Virtual Mouse", frame)
    cv2.waitKey(1)