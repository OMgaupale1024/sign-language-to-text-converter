from flask import Flask, request, jsonify
from flask_cors import CORS
import base64, cv2, numpy as np, io
import os
import math
from PIL import Image
import pyttsx3
from keras.models import load_model
from cvzone.HandTrackingModule import HandDetector

# Check if model file exists
MODEL_FILE = 'cnn8grps_rad1_model.h5'
model = None
classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

if os.path.exists(MODEL_FILE):
    try:
        print(f"Loading model from {MODEL_FILE}...")
        model = load_model(MODEL_FILE)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Server will run but predictions will not work.")
else:
    print(f"ERROR: Model file '{MODEL_FILE}' not found!")
    print("Please ensure the model file is in the root directory.")
    print("Server will start but predictions will return errors.")

app = Flask(__name__)
CORS(app)
tts = pyttsx3.init()

# Initialize hand detectors
hd = HandDetector(maxHands=1)
hd2 = HandDetector(maxHands=1)
offset = 29

def distance(x, y):
    """Calculate Euclidean distance between two points"""
    return math.sqrt(((x[0] - y[0]) ** 2) + ((x[1] - y[1]) ** 2))

def predict_sign_advanced(white_canvas, pts):
    """
    Advanced prediction using the same logic as final_pred.py
    Uses white canvas image and hand landmarks for accurate detection
    """
    if model is None:
        raise ValueError("Model not loaded. Please ensure 'cnn8grps_rad1_model.h5' exists in the root directory.")
    
    if pts is None or len(pts) < 21:
        return '—', 0.0
    
    # Reshape white canvas for prediction (same as final_pred.py)
    white = white_canvas.copy()
    white = white.reshape(1, 400, 400, 3)
    
    # Get model prediction
    prob = np.array(model.predict(white, verbose=0)[0], dtype='float32')
    ch1 = np.argmax(prob, axis=0)
    confidence = float(prob[ch1])  # Store original confidence before modifying
    prob[ch1] = 0
    ch2 = np.argmax(prob, axis=0)
    prob[ch2] = 0
    ch3 = np.argmax(prob, axis=0)
    prob[ch3] = 0
    
    pl = [ch1, ch2]
    
    # All the complex conditions from final_pred.py
    # condition for [Aemnst]
    l = [[5, 2], [5, 3], [3, 5], [3, 6], [3, 0], [3, 2], [6, 4], [6, 1], [6, 2], [6, 6], [6, 7], [6, 0], [6, 5],
         [4, 1], [1, 0], [1, 1], [6, 3], [1, 6], [5, 6], [5, 1], [4, 5], [1, 4], [1, 5], [2, 0], [2, 6], [4, 6],
         [1, 0], [5, 7], [1, 6], [6, 1], [7, 6], [2, 5], [7, 1], [5, 4], [7, 0], [7, 5], [7, 2]]
    if pl in l:
        if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 0

    # condition for [o][s]
    l = [[2, 2], [2, 1]]
    if pl in l:
        if (pts[5][0] < pts[4][0]):
            ch1 = 0

    # condition for [c0][aemnst]
    l = [[0, 0], [0, 6], [0, 2], [0, 5], [0, 1], [0, 7], [5, 2], [7, 6], [7, 1]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[0][0] > pts[8][0] and pts[0][0] > pts[4][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and pts[5][0] > pts[4][0]:
            ch1 = 2

    # condition for [c0][aemnst]
    l = [[6, 0], [6, 6], [6, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if distance(pts[8], pts[16]) < 52:
            ch1 = 2

    # condition for [gh][bdfikruvw]
    l = [[1, 4], [1, 5], [1, 6], [1, 3], [1, 0]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[6][1] > pts[8][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1] and pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]:
            ch1 = 3

    # con for [gh][l]
    l = [[4, 6], [4, 1], [4, 5], [4, 3], [4, 7]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[4][0] > pts[0][0]:
            ch1 = 3

    # con for [gh][pqz]
    l = [[5, 3], [5, 0], [5, 7], [5, 4], [5, 2], [5, 1], [5, 5]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[2][1] + 15 < pts[16][1]:
            ch1 = 3

    # con for [l][x]
    l = [[6, 4], [6, 1], [6, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if distance(pts[4], pts[11]) > 55:
            ch1 = 4

    # con for [l][d]
    l = [[1, 4], [1, 6], [1, 1]]
    pl = [ch1, ch2]
    if pl in l:
        if (distance(pts[4], pts[11]) > 50) and (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 4

    # con for [l][gh]
    l = [[3, 6], [3, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[4][0] < pts[0][0]):
            ch1 = 4

    # con for [l][c0]
    l = [[2, 2], [2, 5], [2, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[1][0] < pts[12][0]):
            ch1 = 4

    # con for [gh][z]
    l = [[3, 6], [3, 5], [3, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] > pts[10][1]:
            ch1 = 5

    # con for [gh][pq]
    l = [[3, 2], [3, 1], [3, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[4][1] + 17 > pts[8][1] and pts[4][1] + 17 > pts[12][1] and pts[4][1] + 17 > pts[16][1] and pts[4][1] + 17 > pts[20][1]:
            ch1 = 5

    # con for [l][pqz]
    l = [[4, 4], [4, 5], [4, 2], [7, 5], [7, 6], [7, 0]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[4][0] > pts[0][0]:
            ch1 = 5

    # con for [pqz][aemnst]
    l = [[0, 2], [0, 6], [0, 1], [0, 5], [0, 0], [0, 7], [0, 4], [0, 3], [2, 7]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[0][0] < pts[8][0] and pts[0][0] < pts[12][0] and pts[0][0] < pts[16][0] and pts[0][0] < pts[20][0]:
            ch1 = 5

    # con for [pqz][yj]
    l = [[5, 7], [5, 2], [5, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[3][0] < pts[0][0]:
            ch1 = 7

    # con for [l][yj]
    l = [[4, 6], [4, 2], [4, 4], [4, 1], [4, 5], [4, 7]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[6][1] < pts[8][1]:
            ch1 = 7

    # con for [x][yj]
    l = [[6, 7], [0, 7], [0, 1], [0, 0], [6, 4], [6, 6], [6, 5], [6, 1]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[18][1] > pts[20][1]:
            ch1 = 7

    # condition for [x][aemnst]
    l = [[0, 4], [0, 2], [0, 3], [0, 1], [0, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[5][0] > pts[16][0]:
            ch1 = 6

    # condition for [yj][x]
    l = [[7, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[18][1] < pts[20][1] and pts[8][1] < pts[10][1]:
            ch1 = 6

    # condition for [c0][x]
    l = [[2, 1], [2, 2], [2, 6], [2, 7], [2, 0]]
    pl = [ch1, ch2]
    if pl in l:
        if distance(pts[8], pts[16]) > 50:
            ch1 = 6

    # con for [l][x]
    l = [[4, 6], [4, 2], [4, 1], [4, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if distance(pts[4], pts[11]) < 60:
            ch1 = 6

    # con for [x][d]
    l = [[1, 4], [1, 6], [1, 0], [1, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[5][0] - pts[4][0] - 15 > 0:
            ch1 = 6

    # con for [b][pqz]
    l = [[5, 0], [5, 1], [5, 4], [5, 5], [5, 6], [6, 1], [7, 6], [0, 2], [7, 1], [7, 4], [6, 6], [7, 2], [5, 0],
         [6, 3], [6, 4], [7, 5], [7, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 1

    # con for [f][pqz]
    l = [[6, 1], [6, 0], [0, 3], [6, 4], [2, 2], [0, 6], [6, 2], [7, 6], [4, 6], [4, 1], [4, 2], [0, 2], [7, 1],
         [7, 4], [6, 6], [7, 2], [7, 5], [7, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 1

    l = [[6, 1], [6, 0], [4, 2], [4, 1], [4, 6], [4, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 1

    # con for [d][pqz]
    l = [[5, 0], [3, 4], [3, 0], [3, 1], [3, 5], [5, 5], [5, 4], [5, 1], [7, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[4][1] > pts[14][1]):
            ch1 = 1

    l = [[4, 1], [4, 2], [4, 4]]
    pl = [ch1, ch2]
    if pl in l:
        if (distance(pts[4], pts[11]) < 50) and (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 1

    l = [[3, 4], [3, 0], [3, 1], [3, 5], [3, 6]]
    pl = [ch1, ch2]
    if pl in l:
        if ((pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[2][0] < pts[0][0]) and pts[14][1] < pts[4][1]):
            ch1 = 1

    l = [[6, 6], [6, 4], [6, 1], [6, 2]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[5][0] - pts[4][0] - 15 < 0:
            ch1 = 1

    # con for [i][pqz]
    l = [[5, 4], [5, 5], [5, 1], [0, 3], [0, 7], [5, 0], [0, 2], [6, 2], [7, 5], [7, 1], [7, 6], [7, 7]]
    pl = [ch1, ch2]
    if pl in l:
        if ((pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1])):
            ch1 = 1

    # con for [yj][bfdi]
    l = [[1, 5], [1, 7], [1, 1], [1, 6], [1, 3], [1, 0]]
    pl = [ch1, ch2]
    if pl in l:
        if (pts[4][0] < pts[5][0] + 15) and ((pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1])):
            ch1 = 7

    # con for [uvr]
    l = [[5, 5], [5, 0], [5, 4], [5, 1], [4, 6], [4, 1], [7, 6], [3, 0], [3, 5]]
    pl = [ch1, ch2]
    if pl in l:
        if ((pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1])) and pts[4][1] > pts[14][1]:
            ch1 = 1

    # con for [w]
    fg = 13
    l = [[3, 5], [3, 0], [3, 6], [5, 1], [4, 1], [2, 0], [5, 0], [5, 5]]
    pl = [ch1, ch2]
    if pl in l:
        if not (pts[0][0] + fg < pts[8][0] and pts[0][0] + fg < pts[12][0] and pts[0][0] + fg < pts[16][0] and pts[0][0] + fg < pts[20][0]) and not (pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and distance(pts[4], pts[11]) < 50:
            ch1 = 1

    # con for [w]
    l = [[5, 0], [5, 5], [0, 1]]
    pl = [ch1, ch2]
    if pl in l:
        if pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1]:
            ch1 = 1

    # Convert group numbers to letters
    if ch1 == 0:
        ch1 = 'S'
        if pts[4][0] < pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0]:
            ch1 = 'A'
        if pts[4][0] > pts[6][0] and pts[4][0] < pts[10][0] and pts[4][0] < pts[14][0] and pts[4][0] < pts[18][0] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]:
            ch1 = 'T'
        if pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1] and pts[4][1] > pts[16][1] and pts[4][1] > pts[20][1]:
            ch1 = 'E'
        if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][0] > pts[14][0] and pts[4][1] < pts[18][1]:
            ch1 = 'M'
        if pts[4][0] > pts[6][0] and pts[4][0] > pts[10][0] and pts[4][1] < pts[18][1] and pts[4][1] < pts[14][1]:
            ch1 = 'N'

    if ch1 == 2:
        if distance(pts[12], pts[4]) > 42:
            ch1 = 'C'
        else:
            ch1 = 'O'

    if ch1 == 3:
        if (distance(pts[8], pts[12])) > 72:
            ch1 = 'G'
        else:
            ch1 = 'H'

    if ch1 == 7:
        if distance(pts[8], pts[4]) > 42:
            ch1 = 'Y'
        else:
            ch1 = 'J'

    if ch1 == 4:
        ch1 = 'L'

    if ch1 == 6:
        ch1 = 'X'

    if ch1 == 5:
        if pts[4][0] > pts[12][0] and pts[4][0] > pts[16][0] and pts[4][0] > pts[20][0]:
            if pts[8][1] < pts[5][1]:
                ch1 = 'Z'
            else:
                ch1 = 'Q'
        else:
            ch1 = 'P'

    if ch1 == 1:
        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 'B'
        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'D'
        if (pts[6][1] < pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 'F'
        if (pts[6][1] < pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = 'I'
        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] > pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'W'
        if (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and pts[4][1] < pts[9][1]:
            ch1 = 'K'
        if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) < 8) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'U'
        if ((distance(pts[8], pts[12]) - distance(pts[6], pts[10])) >= 8) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]) and (pts[4][1] > pts[9][1]):
            ch1 = 'V'
        if (pts[8][0] > pts[12][0]) and (pts[6][1] > pts[8][1] and pts[10][1] > pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] < pts[20][1]):
            ch1 = 'R'

    # Space detection
    if ch1 == 1 or ch1 == 'E' or ch1 == 'S' or ch1 == 'X' or ch1 == 'Y' or ch1 == 'B':
        if (pts[6][1] > pts[8][1] and pts[10][1] < pts[12][1] and pts[14][1] < pts[16][1] and pts[18][1] > pts[20][1]):
            ch1 = " "

    # "Confirm" gesture detection - Open Palm (all fingers extended upward)
    # This gesture confirms/accepts the current letter (allows duplicates)
    # Palm gesture: All fingers extended and pointing up, palm facing camera
    # Check: All fingertips are above their base joints, and thumb is extended
    if (pts[4][1] < pts[3][1] and  # Thumb tip above thumb base
        pts[8][1] < pts[6][1] and  # Index finger tip above base
        pts[12][1] < pts[10][1] and  # Middle finger tip above base
        pts[16][1] < pts[14][1] and  # Ring finger tip above base
        pts[20][1] < pts[18][1] and  # Pinky tip above base
        pts[0][1] < pts[5][1] and  # Wrist above index base (palm facing up/forward)
        pts[0][1] < pts[9][1] and  # Wrist above middle base
        pts[0][1] < pts[13][1]):  # Wrist above ring base
        ch1 = "confirm"

    # Backspace gesture detection
    if ch1 == 'B' or ch1 == 'C' or ch1 == 'H' or ch1 == 'F' or ch1 == 'X':
        if (pts[0][0] > pts[8][0] and pts[0][0] > pts[12][0] and pts[0][0] > pts[16][0] and pts[0][0] > pts[20][0]) and \
           (pts[4][1] < pts[8][1] and pts[4][1] < pts[12][1] and pts[4][1] < pts[16][1] and pts[4][1] < pts[20][1]) and \
           (pts[4][1] < pts[6][1] and pts[4][1] < pts[10][1] and pts[4][1] < pts[14][1] and pts[4][1] < pts[18][1]):
            ch1 = 'Backspace'

    return str(ch1), confidence

def draw_hand_skeleton(frame):
    """
    Draw hand skeleton on white canvas and return landmarks
    Returns: (white_canvas, landmarks_list)
    Matches the exact logic from final_pred.py
    """
    white = np.ones((400, 400, 3), np.uint8) * 255
    pts = None
    
    try:
        # Flip frame horizontally (same as final_pred.py)
        frame = cv2.flip(frame, 1)
        
        # Find hands (cvzone returns tuple or list)
        hands_result = hd.findHands(frame, draw=False, flipType=True)
        
        # Handle different return types from cvzone
        if isinstance(hands_result, tuple):
            hands = hands_result[0] if hands_result[0] else []
        else:
            hands = hands_result if hands_result else []
        
        if hands and len(hands) > 0:
            # Structure exactly like final_pred.py: hands[0] is a list, hands[0][0] is the map
            hand = hands[0]
            if isinstance(hand, list) and len(hand) > 0:
                hand_map = hand[0]
                x, y, w, h = hand_map['bbox']
            elif isinstance(hand, dict) and 'bbox' in hand:
                # Direct dict structure
                x, y, w, h = hand['bbox']
            else:
                # Try as direct dict
                hand_map = hand if isinstance(hand, dict) else hand[0] if isinstance(hand, list) else {}
                x, y, w, h = hand_map.get('bbox', (0, 0, 0, 0))
            
            # Extract hand region with offset
            y_start = max(0, y - offset)
            y_end = min(frame.shape[0], y + h + offset)
            x_start = max(0, x - offset)
            x_end = min(frame.shape[1], x + w + offset)
            
            if y_end > y_start and x_end > x_start:
                image = frame[y_start:y_end, x_start:x_end]
                
                if image.size > 0 and len(image.shape) == 3:
                    # Second hand detection on cropped image
                    handz_result = hd2.findHands(image, draw=False, flipType=True)
                    
                    # Handle different return types
                    if isinstance(handz_result, tuple):
                        handz = handz_result[0] if handz_result[0] else []
                    else:
                        handz = handz_result if handz_result else []
                    
                    if handz and len(handz) > 0:
                        # Structure exactly like final_pred.py: handz[0] is a list, handz[0][0] is the map
                        hand = handz[0]
                        if isinstance(hand, list) and len(hand) > 0:
                            hand_map = hand[0]
                            pts = hand_map['lmList']
                        elif isinstance(hand, dict) and 'lmList' in hand:
                            # Direct dict structure
                            pts = hand['lmList']
                        else:
                            # Try as direct dict
                            hand_map = hand if isinstance(hand, dict) else hand[0] if isinstance(hand, list) else {}
                            pts = hand_map.get('lmList', None)
                        
                        if pts and len(pts) >= 21:
                            os = ((400 - w) // 2) - 15
                            os1 = ((400 - h) // 2) - 15
                            
                            # Draw finger lines
                            for t in range(0, 4, 1):
                                cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), 
                                        (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                            for t in range(5, 8, 1):
                                cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), 
                                        (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                            for t in range(9, 12, 1):
                                cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), 
                                        (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                            for t in range(13, 16, 1):
                                cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), 
                                        (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                            for t in range(17, 20, 1):
                                cv2.line(white, (pts[t][0] + os, pts[t][1] + os1), 
                                        (pts[t + 1][0] + os, pts[t + 1][1] + os1), (0, 255, 0), 3)
                            
                            # Draw palm lines
                            cv2.line(white, (pts[5][0] + os, pts[5][1] + os1), 
                                    (pts[9][0] + os, pts[9][1] + os1), (0, 255, 0), 3)
                            cv2.line(white, (pts[9][0] + os, pts[9][1] + os1), 
                                    (pts[13][0] + os, pts[13][1] + os1), (0, 255, 0), 3)
                            cv2.line(white, (pts[13][0] + os, pts[13][1] + os1), 
                                    (pts[17][0] + os, pts[17][1] + os1), (0, 255, 0), 3)
                            cv2.line(white, (pts[0][0] + os, pts[0][1] + os1), 
                                    (pts[5][0] + os, pts[5][1] + os1), (0, 255, 0), 3)
                            cv2.line(white, (pts[0][0] + os, pts[0][1] + os1), 
                                    (pts[17][0] + os, pts[17][1] + os1), (0, 255, 0), 3)
                            
                            # Draw joints
                            for i in range(21):
                                cv2.circle(white, (pts[i][0] + os, pts[i][1] + os1), 2, (0, 0, 255), 1)
    except Exception as e:
        print(f"Error drawing skeleton: {e}")
        import traceback
        traceback.print_exc()
    
    return white, pts

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if model is None:
            return jsonify({
                'error': 'Model not loaded',
                'message': 'Please ensure cnn8grps_rad1_model.h5 exists in the root directory'
            }), 503
        
        data = request.json
        if 'image' not in data:
            return jsonify({'error': 'no image provided'}), 400
        
        img_data = base64.b64decode(data['image'].split(',')[1])
        img = Image.open(io.BytesIO(img_data)).convert('RGB')
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Debug: Check frame dimensions
        if frame is None or frame.size == 0:
            return jsonify({'error': 'Invalid frame received'}), 400
        
        # Get hand skeleton and landmarks (same as final_pred.py)
        white_canvas, pts = draw_hand_skeleton(frame)
        
        # Use advanced prediction with white canvas and landmarks
        if pts is not None and len(pts) >= 21:
            try:
                predicted, confidence = predict_sign_advanced(white_canvas, pts)
            except Exception as pred_error:
                print(f"Prediction error: {pred_error}")
                import traceback
                traceback.print_exc()
                predicted = '—'
                confidence = 0.0
        else:
            predicted = '—'
            confidence = 0.0
            if pts is None:
                print("No hand detected - pts is None")
            elif len(pts) < 21:
                print(f"Not enough landmarks - got {len(pts) if pts else 0} points")
        
        # Encode white canvas to base64
        _, buffer = cv2.imencode('.jpg', white_canvas)
        white_canvas_b64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'text': predicted,
            'confidence': confidence,
            'white_canvas': f'data:image/jpeg;base64,{white_canvas_b64}',
            'skeleton': f'data:image/jpeg;base64,{white_canvas_b64}',
            'hand_detected': pts is not None and len(pts) >= 21
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/detect', methods=['POST'])
def detect():
    if model is None:
        return jsonify({
            'error': 'Model not loaded',
            'message': 'Please ensure cnn8grps_rad1_model.h5 exists in the root directory'
        }), 503
    
    data = request.json
    if 'image' not in data:
        return jsonify({'error': 'no image provided'}), 400

    try:
        img_data = base64.b64decode(data['image'].split(',')[1])
        img = Image.open(io.BytesIO(img_data)).convert('RGB')
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Get hand skeleton and landmarks
        white_canvas, pts = draw_hand_skeleton(frame)
        
        # Use advanced prediction
        if pts is not None and len(pts) >= 21:
            predicted, confidence = predict_sign_advanced(white_canvas, pts)
        else:
            predicted = '—'
            confidence = 0.0
            
        return jsonify({'text': predicted, 'confidence': confidence})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    if text:
        tts.say(text)
        tts.runAndWait()
    return jsonify({'message': 'spoken'})

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'model_loaded': model is not None,
        'model_file': MODEL_FILE,
        'model_exists': os.path.exists(MODEL_FILE)
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SignSpeak Backend Server")
    print("="*60)
    if model is None:
        print("\n⚠️  WARNING: Model not loaded!")
        print(f"   Model file '{MODEL_FILE}' not found.")
        print("   The server will start but predictions will fail.")
        print("   Please place the model file in the root directory.\n")
    else:
        print("\n✅ Model loaded successfully!")
        print("   Server ready to accept requests.\n")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000)
