# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QbDVuOedgYOWXG10oN_mVYHH_la6Nmeu
"""

import cv2
import numpy as np
import mediapipe as mp
import streamlit as st
from collections import deque

# Initialize MediaPipe and variables
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Deques to store points for different colors
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]

blue_index = green_index = red_index = yellow_index = 0
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0

# Initialize the canvas
paintWindow = np.zeros((480, 640, 3), np.uint8) + 255

# Streamlit UI elements
st.title("Hand Drawing with Cloudsketch 🎨✋")
st.write("Use your finger to draw. Press 'Clear' to clear the canvas.")

# Color selection buttons
color = st.radio("Select Drawing Color", ('Blue', 'Green', 'Red', 'Yellow'))

if color == 'Blue':
    colorIndex = 0
elif color == 'Green':
    colorIndex = 1
elif color == 'Red':
    colorIndex = 2
elif color == 'Yellow':
    colorIndex = 3

# Button to clear the canvas
clear_canvas = st.button("Clear Canvas")

# Webcam input using Streamlit
FRAME_WINDOW = st.image([])
cap = cv2.VideoCapture(0)

# Main loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        st.write("Failed to capture video")
        break

    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(framergb)

    if result.multi_hand_landmarks:
        for handslms in result.multi_hand_landmarks:
            # Draw landmarks and connections with red dots and lines
            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS,
                                  mpDraw.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=3),
                                  mpDraw.DrawingSpec(color=(0, 0, 255), thickness=2))

            landmarks = []
            for lm in handslms.landmark:
                lmx = int(lm.x * 640)
                lmy = int(lm.y * 480)
                landmarks.append([lmx, lmy])

            fore_finger = (landmarks[8][0], landmarks[8][1])
            thumb = (landmarks[4][0], landmarks[4][1])

            # Ensure the deques are initialized
            if not bpoints:
                bpoints.append(deque(maxlen=1024))
            if not gpoints:
                gpoints.append(deque(maxlen=1024))
            if not rpoints:
                rpoints.append(deque(maxlen=1024))
            if not ypoints:
                ypoints.append(deque(maxlen=1024))

            # Check if thumb is close to the forefinger to start a new line
            if (thumb[1] - fore_finger[1] < 30):
                if colorIndex == 0:
                    bpoints.append(deque(maxlen=512))
                elif colorIndex == 1:
                    gpoints.append(deque(maxlen=512))
                elif colorIndex == 2:
                    rpoints.append(deque(maxlen=512))
                elif colorIndex == 3:
                    ypoints.append(deque(maxlen=512))
            else:
                # Append points based on selected color
                if colorIndex == 0:
                    bpoints[-1].appendleft(fore_finger)
                elif colorIndex == 1:
                    gpoints[-1].appendleft(fore_finger)
                elif colorIndex == 2:
                    rpoints[-1].appendleft(fore_finger)
                elif colorIndex == 3:
                    ypoints[-1].appendleft(fore_finger)

    # Draw lines on the frame
    points = [bpoints, gpoints, rpoints, ypoints]
    for i, point in enumerate(points):
        for j in range(len(point)):
            for k in range(1, len(point[j])):
                if point[j][k - 1] is None or point[j][k] is None:
                    continue
                cv2.line(frame, point[j][k - 1], point[j][k], colors[i], 2)

    # Clear the canvas if the button is pressed
    if clear_canvas:
        bpoints, gpoints, rpoints, ypoints = [deque(maxlen=1024) for _ in range(4)]
        paintWindow = np.zeros((480, 640, 3), np.uint8) + 255

    # Display the frame in Streamlit
    FRAME_WINDOW.image(frame, channels="BGR")

cap.release()