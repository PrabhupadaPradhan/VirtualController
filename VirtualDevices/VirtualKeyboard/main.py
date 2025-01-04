import cv2
import numpy as np
import mediapipe as mp
import pyautogui as pyg

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Virtual keyboard layout
keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "{", "}", "[", "]"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "BackSpace"],
    ["CapsLock", "A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Shift", "Z", "X", "C", "V", "B", "N", "M"],
    ["#", "Space", "@"]
]

# Keyboard settings
key_width = 80
key_height = 80
margin = 0
keyboard_origin = (350, 300)  # Top-left corner of the keyboard
output_text = ""  # To store output text



# change in size for different key
def key_sizes(r, c):
    k = keys[r][c]
    if k == "Space":
        return 100
    if k == "Tab":
        return 40
    if k == "CapsLock":
        return 70
    if k =="Shift":
        return 50
    return 20

def rect_sizes(r, c):
    k = keys[r][c]
    if k == "Space":
        return 265
    return 80

# function to draw the virtual keyboard
def draw_keyboard(frame, hover_key=None):
    x_start, y_start = keyboard_origin
    for row_idx, row in enumerate(keys):
        for col_idx, key in enumerate(row):
            y = y_start + row_idx * (key_height + margin)
            x = x_start + sum([rect_sizes(row_idx, i) for i in range(col_idx)])
            color = (0, 255, 0) if (row_idx, col_idx) == hover_key else (255, 255, 255)
            cv2.rectangle(frame, (x, y), (x + rect_sizes(row_idx, col_idx), y + key_height), color, -1 if (row_idx, col_idx) == hover_key else 2)
            cv2.putText(frame, key, (x + key_sizes(row_idx, col_idx), y + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# function to find the key being hovered
def get_hovered_key(hand_x, hand_y):
    x_start, y_start = keyboard_origin
    for row_idx, row in enumerate(keys):
        for col_idx, key in enumerate(row):
            x = x_start + sum([rect_sizes(row_idx, i) for i in range(col_idx)])
            y = y_start + row_idx * (key_height + margin)
            if x <= hand_x <= x + rect_sizes(row_idx, col_idx) and y <= hand_y <= y + key_height:
                return (row_idx, col_idx)
    return None

# Main loop
cap = cv2.VideoCapture(0)
click_delay = 10  # Delay in frames to register subsequent clicks
click_timer = 0   # Timer to control click frequency

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)  # Flip for a mirror effect
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Mediapipe processing
    result = hands.process(rgb_frame)
    hover_key = None

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get index and middle finger tip coordinates
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            x_index, y_index = int(index_tip.x * w), int(index_tip.y * h)
            x_middle, y_middle = int(middle_tip.x * w), int(middle_tip.y * h)
            
            # Check if hovering over a key
            hover_key = get_hovered_key(x_index, y_index)
            
            # Check if index and middle fingers are close together (click condition)
            distance = np.sqrt((x_index - x_middle)**2 + (y_index - y_middle)**2)
            if distance < 40 and hover_key and click_timer == 0:
                row, col = hover_key
                key = keys[row][col] if keys[row][col] != "Space" else " "
                output_text += key  # Add clicked key to output text
                click_timer = click_delay  # Reset click timer

                # Visualize pressing action
                cv2.circle(frame, (x_index, y_index), 10, (0, 0, 255), -1)
                cv2.circle(frame, (x_middle, y_middle), 10, (0, 0, 255), -1)

    # Reduce click timer
    if click_timer > 0:
        click_timer -= 1

    # Draw keyboard
    draw_keyboard(frame, hover_key)

    # Display output text
    output_box_origin = (400, 800)
    cv2.rectangle(frame, output_box_origin, (1200, 1000), (255, 255, 255, 0), -1)
    output_list = []
    cnt = 0
    temp = ""
    limit = 30
    for i in output_text:
        temp += i
        cnt += 1
        if cnt == limit:
            output_list.append(temp)
            cnt = 0
            temp = ""
    if len(temp) > 0:
        output_list.append(temp)
    for i in range(len(output_list)):
        cv2.putText(
            frame, ("Output: " if i == 0 else " " * 8) + output_list[i],
            (output_box_origin[0] + 10, output_box_origin[1] + 50 * (i + 1)),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2
        )
    cv2.imshow("Virtual Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Press Esc to exit
        break
cap.release()
cv2.destroyAllWindows()