import cv2
import time
import threading
import numpy as np
import pyautogui
from gestures.hand_tracker import HandTracker

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001


class GestureController:
    def __init__(self, camera_idx=0, frame_r=70, smooth_val=2.2, click_dist=38):
        self.camera_idx = camera_idx
        self.frame_r = frame_r  # Boshqaruv maydoni chegarasi
        self.smooth_val = max(1.0, float(smooth_val))
        self.click_dist = click_dist
        
        self.is_running = False
        self.is_enabled = True  # Standart holda FAOL
        self.thread = None
        self.cap = None
        
        self.screen_w, self.screen_h = pyautogui.size()
        self.cam_w, self.cam_h = 640, 480
        
        self.prev_x, self.prev_y = self.screen_w // 2, self.screen_h // 2
        self.curr_x, self.curr_y = self.screen_w // 2, self.screen_h // 2
        
        self.last_click_time = 0
        self.last_dual_gesture_time = 0
        self.is_dragging = False
        self.fist_start_time = 0
        self.current_action = "Qo'llar kutilmoqda"
        
        self.tracker = None
        self.on_frame_callback = None

    def set_frame_callback(self, cb):
        self.on_frame_callback = cb

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_enabled = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.is_enabled = False
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass

    def enable(self):
        self.is_enabled = True
        return True

    def disable(self):
        self.is_enabled = False
        self.current_action = "O'chiq"
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False
        return False

    def toggle(self):
        if self.is_enabled:
            return self.disable()
        else:
            return self.enable()

    def _open_camera(self):
        cap = cv2.VideoCapture(self.camera_idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_idx)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_h)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 30)
        for _ in range(2):
            cap.read()
        return cap

    def _run_loop(self):
        # 2 ta qo'lni parallel kuzatish (max_hands=2)
        self.tracker = HandTracker(max_hands=2, detection_con=0.55, track_con=0.55)
        self.cap = self._open_camera()
        prev_scroll_y = None
        consecutive_failures = 0
        prev_hands_dist = None

        while self.is_running:
            if not self.is_enabled:
                time.sleep(0.08)
                continue

            if not self.cap or not self.cap.isOpened():
                self.cap = self._open_camera()
                time.sleep(0.2)
                continue

            success, img = self.cap.read()
            if not success or img is None:
                consecutive_failures += 1
                if consecutive_failures > 8:
                    if self.cap:
                        self.cap.release()
                    self.cap = self._open_camera()
                    consecutive_failures = 0
                time.sleep(0.02)
                continue
            
            try:
                consecutive_failures = 0
                now = time.time()

                # Mirror
                img = cv2.flip(img, 1)
                h, w, _ = img.shape
                
                # Kursor maydoni chegarasi
                cv2.rectangle(
                    img, 
                    (self.frame_r, self.frame_r), 
                    (w - self.frame_r, h - self.frame_r), 
                    (0, 240, 255), 2
                )

                # Qo'llarni aniqlash
                img = self.tracker.find_hands(img, draw=True)
                all_hands = self.tracker.find_all_hands(img)

                action_text = "Qo'lingizni kamera maydoniga tuting"
                action_color = (180, 180, 180)

                # ==========================================================
                # 1. IKKALA QO'L ISHLAGANDA (DUAL HAND GESTURES)
                # ==========================================================
                if len(all_hands) >= 2:
                    h1, h2 = all_hands[0], all_hands[1]
                    f1 = self.tracker.fingers_up(h1)
                    f2 = self.tracker.fingers_up(h2)

                    # Kaftlar orasidagi masofa
                    c1_x, c1_y = h1[9][1], h1[9][2]
                    c2_x, c2_y = h2[9][1], h2[9][2]
                    hands_dist = np.hypot(c2_x - c1_x, c2_y - c1_y)
                    cv2.line(img, (c1_x, c1_y), (c2_x, c2_y), (255, 0, 255), 2)

                    # Ikki musht birga -> Ish stolini ko'rsatish (Win+D)
                    is_fist1 = (sum(f1[1:]) == 0)
                    is_fist2 = (sum(f2[1:]) == 0)

                    if is_fist1 and is_fist2 and (now - self.last_dual_gesture_time) > 1.2:
                        pyautogui.hotkey("win", "d")
                        self.last_dual_gesture_time = now
                        action_text = "👊👊 IKKI MUSHT: ISH STOLI (WIN+D)"
                        action_color = (255, 100, 255)

                    # Ikkala qo'lni yoyish / yaqinlashtirish (Zoom / Maximize / Minimize)
                    elif prev_hands_dist is not None and (now - self.last_dual_gesture_time) > 0.6:
                        dist_diff = hands_dist - prev_hands_dist
                        if dist_diff > 45:  # Qo'llar kengaydi -> Maximize
                            pyautogui.hotkey("win", "up")
                            self.last_dual_gesture_time = now
                            action_text = "👐 IKKI QO'LNI YOYISH: OYNANI KATTALASHTIRISH (MAXIMIZE)"
                            action_color = (0, 255, 255)
                        elif dist_diff < -45:  # Qo'llar yaqinlashdi -> Restore/Minimize
                            pyautogui.hotkey("win", "down")
                            self.last_dual_gesture_time = now
                            action_text = "👏 IKKI QO'LNI YAQLASHTIRISH: OYNANI KICHIKLASHTIRISH"
                            action_color = (255, 200, 0)

                    prev_hands_dist = hands_dist

                else:
                    prev_hands_dist = None

                # ==========================================================
                # 2. ASOSIY QO'L (PRIMARY HAND) HARAKATLARI VA DRAG & DROP
                # ==========================================================
                if len(all_hands) >= 1:
                    lm_list = all_hands[0]
                    fingers = self.tracker.fingers_up(lm_list)

                    x1, y1 = lm_list[8][1], lm_list[8][2]   # Index tip
                    x2, y2 = lm_list[4][1], lm_list[4][2]   # Thumb tip
                    x3, y3 = lm_list[12][1], lm_list[12][2] # Middle tip
                    knuckle_x, knuckle_y = lm_list[9][1], lm_list[9][2] # Middle knuckle

                    palm_scale = max(30.0, float(np.hypot(lm_list[0][1] - lm_list[9][1], lm_list[0][2] - lm_list[9][2])))
                    is_fist = (fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0)

                    # 1. MUSHT BO'LGANDA -> OYNANI USHLAB SILJITISH (DRAG & DROP)
                    if is_fist:
                        cv2.circle(img, (knuckle_x, knuckle_y), 24, (0, 255, 120), cv2.FILLED)
                        cv2.putText(img, "FIST", (knuckle_x - 20, knuckle_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                        
                        if self.fist_start_time == 0:
                            self.fist_start_time = now

                        # Musht koordinatasini ekranga o'tkazish
                        x_mapped = np.interp(knuckle_x, (self.frame_r, w - self.frame_r), (0, self.screen_w))
                        y_mapped = np.interp(knuckle_y, (self.frame_r, h - self.frame_r), (0, self.screen_h))

                        self.curr_x = self.prev_x + (x_mapped - self.prev_x) / 1.5
                        self.curr_y = self.prev_y + (y_mapped - self.prev_y) / 1.5

                        # 0.18s dan ortiq ushlab turilsa -> DRAG FAOL VA KURSOR BILAN OYNA SURILADI!
                        if (now - self.fist_start_time) > 0.18:
                            if not self.is_dragging:
                                pyautogui.mouseDown()
                                self.is_dragging = True
                            
                            # SILJITISH (Oyna siljishi uchun kursor ko'chiriladi)
                            pyautogui.moveTo(self.curr_x, self.curr_y)
                            self.prev_x, self.prev_y = self.curr_x, self.curr_y
                            action_text = "✊ MUSHT: OYNA USHLANDI VA SILJITILMOQDA..."
                            action_color = (0, 255, 120)
                        else:
                            action_text = "✊ MUSHT: USHLASH TAYYORLANMOQDA"
                            action_color = (0, 255, 200)

                    else:
                        # Musht ochilganda darhol qo'yib yuborish (DROP!)
                        if self.is_dragging:
                            pyautogui.mouseUp()
                            self.is_dragging = False
                            action_text = "✋ MUSHT OCHILDI (OYNA QO'YIB YUBORILDI!)"
                            action_color = (0, 255, 0)
                        elif self.fist_start_time > 0 and (now - self.fist_start_time) <= 0.18:
                            # Juda tez musht qilib ochish -> Tezkor CLICK
                            if (now - self.last_click_time) > 0.16:
                                pyautogui.click()
                                self.last_click_time = now
                                action_text = "✊ TEZKOR CLICK BO'LDI!"
                                action_color = (0, 255, 0)
                        self.fist_start_time = 0

                    # 2. KO'RSATKICH BARMOQ HARAKATI (INDEX FINGER CURSOR)
                    if fingers[1] == 1 and fingers[2] == 0 and not is_fist and not self.is_dragging:
                        action_text = "☝️ KO'RSATKICH BARMOQ (KURSOR)"
                        action_color = (0, 255, 255)

                        x_mapped = np.interp(x1, (self.frame_r, w - self.frame_r), (0, self.screen_w))
                        y_mapped = np.interp(y1, (self.frame_r, h - self.frame_r), (0, self.screen_h))

                        dist_delta = np.hypot(x_mapped - self.prev_x, y_mapped - self.prev_y)
                        dynamic_smooth = max(1.1, self.smooth_val if dist_delta < 35 else 1.3)

                        self.curr_x = self.prev_x + (x_mapped - self.prev_x) / dynamic_smooth
                        self.curr_y = self.prev_y + (y_mapped - self.prev_y) / dynamic_smooth

                        pyautogui.moveTo(self.curr_x, self.curr_y)
                        cv2.circle(img, (x1, y1), 12, (0, 255, 255), cv2.FILLED)
                        cv2.drawMarker(img, (x1, y1), (0, 255, 0), cv2.MARKER_CROSS, 22, 2)
                        self.prev_x, self.prev_y = self.curr_x, self.curr_y

                    # 3. PINCH CLICK (Bosh + Ko'rsatkich barmoq tekkanda)
                    dist_pinch, info_pinch = self.tracker.calculate_distance(lm_list[4], lm_list[8], img=img, draw=False)
                    ratio_pinch = dist_pinch / palm_scale

                    if not is_fist and not self.is_dragging and (ratio_pinch < 0.28 or dist_pinch < self.click_dist):
                        cv2.circle(img, (info_pinch[4], info_pinch[5]), 15, (0, 255, 0), cv2.FILLED)
                        if (now - self.last_click_time) > 0.22:
                            pyautogui.click()
                            self.last_click_time = now
                            action_text = "👌 PINCH CLICK!"
                            action_color = (0, 255, 0)

                    # 4. O'NG TUGMA (RIGHT CLICK) (Bosh + O'rta barmoq)
                    dist_rc, info_rc = self.tracker.calculate_distance(lm_list[4], lm_list[12], img=img, draw=False)
                    ratio_rc = dist_rc / palm_scale
                    if not is_fist and not self.is_dragging and (ratio_rc < 0.28 or dist_rc < self.click_dist):
                        if (now - self.last_click_time) > 0.28:
                            pyautogui.rightClick()
                            self.last_click_time = now
                            cv2.circle(img, (info_rc[4], info_rc[5]), 15, (255, 0, 100), cv2.FILLED)
                            action_text = "🤞 O'NG TUGMA (RIGHT CLICK!)"
                            action_color = (255, 0, 100)

                    # 5. SKROLL (2 barmoq: Ko'rsatkich + O'rta barmoq)
                    if not is_fist and not self.is_dragging and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                        action_text = "✌️ SKROLL QILISH"
                        action_color = (255, 200, 0)
                        cv2.circle(img, (x1, y1), 8, (255, 200, 0), cv2.FILLED)
                        cv2.circle(img, (x3, y3), 8, (255, 200, 0), cv2.FILLED)
                        if prev_scroll_y is not None:
                            delta = prev_scroll_y - y1
                            if abs(delta) > 4:
                                scroll_amount = int(delta * 7)
                                pyautogui.scroll(scroll_amount)
                        prev_scroll_y = y1
                    else:
                        prev_scroll_y = None

                self.current_action = action_text

                # HUD yozuvlari
                hands_count = len(all_hands)
                hands_info = f"({hands_count} ta qo'l faol)" if hands_count > 0 else "(Kutilmoqda)"
                cv2.putText(img, f"STATUS: {action_text} {hands_info}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.60, action_color, 2)
                cv2.putText(img, "IKKI QO'L BILAN BOSHQARUV + OYNA SILJITISH (DRAG) FAOL", (15, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 150), 1)

                # UI callback
                if self.on_frame_callback:
                    try:
                        self.on_frame_callback(img)
                    except Exception:
                        pass
            except Exception:
                pass

            time.sleep(0.004)

        if self.cap:
            self.cap.release()
