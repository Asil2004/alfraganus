import cv2
import math
import numpy as np
from pathlib import Path
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = str(Path(__file__).resolve().parent / "hand_landmarker.task")

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Bosh barmoq
    (0, 5), (5, 6), (6, 7), (7, 8),        # Ko'rsatkich barmoq
    (5, 9), (9, 10), (10, 11), (11, 12),   # O'rta barmoq
    (9, 13), (13, 14), (14, 15), (15, 16), # Nomsiz barmoq
    (13, 17), (17, 18), (18, 19), (19, 20),# Kichik barmoq
    (0, 17)                                # Kaft asosi
]


class HandTracker:
    def __init__(self, max_hands=2, detection_con=0.55, track_con=0.55):
        self.max_hands = max_hands
        self.results = None

        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=self.max_hands,
            min_hand_detection_confidence=detection_con,
            min_hand_presence_confidence=track_con
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def find_hands(self, img, draw=True):
        h, w, c = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        self.results = self.detector.detect(mp_image)

        if self.results and self.results.hand_landmarks and draw:
            for hand_idx, hand_landmarks in enumerate(self.results.hand_landmarks):
                # O'ng qo'l va Chap qo'l uchun alohida ranglar
                line_color = (0, 200, 255) if hand_idx == 0 else (255, 150, 0)
                joint_color = (0, 255, 150) if hand_idx == 0 else (255, 220, 50)

                # Chiziqlarni chizish
                for p1_idx, p2_idx in HAND_CONNECTIONS:
                    pt1 = hand_landmarks[p1_idx]
                    pt2 = hand_landmarks[p2_idx]
                    x1, y1 = int(pt1.x * w), int(pt1.y * h)
                    x2, y2 = int(pt2.x * w), int(pt2.y * h)
                    cv2.line(img, (x1, y1), (x2, y2), line_color, 2)

                # Bo'g'in nuqtalarini chizish
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 4, joint_color, cv2.FILLED)
        return img

    def find_positions(self, img, hand_no=0):
        lm_list = []
        if self.results and self.results.hand_landmarks:
            if hand_no < len(self.results.hand_landmarks):
                my_hand = self.results.hand_landmarks[hand_no]
                h, w, c = img.shape
                for idx, lm in enumerate(my_hand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([idx, cx, cy, lm.z])
        return lm_list

    def find_all_hands(self, img):
        """Kamerada ko'ringan barcha (1 yoki 2 ta) qo'llar koordinatasini ro'yxat qilib qaytaradi"""
        all_hands = []
        if self.results and self.results.hand_landmarks:
            h, w, c = img.shape
            for hand_landmarks in self.results.hand_landmarks:
                lm_list = []
                for idx, lm in enumerate(hand_landmarks):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([idx, cx, cy, lm.z])
                all_hands.append(lm_list)
        return all_hands

    def fingers_up(self, lm_list):
        if not lm_list or len(lm_list) < 21:
            return [0, 0, 0, 0, 0]

        tip_ids = [4, 8, 12, 16, 20]
        fingers = []

        # Bosh barmoq (Ikkala qo'l uchun universal hisoblash)
        # Bosh barmoq uchi (4) bilan kichik barmoq asosi (17) orasidagi masofa
        dist_tip = math.hypot(lm_list[4][1] - lm_list[17][1], lm_list[4][2] - lm_list[17][2])
        dist_ip = math.hypot(lm_list[3][1] - lm_list[17][1], lm_list[3][2] - lm_list[17][2])
        if dist_tip > dist_ip:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 ta barmoq (Index, Middle, Ring, Pinky)
        for id in range(1, 5):
            if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    def calculate_distance(self, p1, p2, img=None, draw=True):
        x1, y1 = p1[1], p1[2]
        x2, y2 = p2[1], p2[2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)

        if draw and img is not None:
            cv2.circle(img, (x1, y1), 6, (255, 0, 128), cv2.FILLED)
            cv2.circle(img, (x2, y2), 6, (255, 0, 128), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 128), 2)
            cv2.circle(img, (cx, cy), 6, (0, 255, 0), cv2.FILLED)

        return length, [x1, y1, x2, y2, cx, cy]
