import os
import sys
import time
import math
import random
import threading
import tkinter as tk
from PIL import Image, ImageTk
import psutil

# Color Palette: Cosmic Islamic Astronomy (Alfraganus theme)
C_BG        = "#040914"  # Chuqur kosmik qora-ko'k
C_PANEL     = "#0a1526"  # Panel foni
C_BORDER    = "#112a45"  # Ramka
C_CYAN      = "#00f0ff"  # Bosh yorqin neon ko'k
C_EMERALD   = "#00ffa3"  # Zumrad yashil (faol holat)
C_GOLD      = "#ffd700"  # Oltin (Alfraganus aksent)
C_TEXT      = "#cceeff"  # Asosiy matn
C_MUTED     = "#5c7d99"  # Xira matn
C_RED       = "#ff3366"  # Xatolik / o'chiq


class AlfraganusUI:
    def __init__(self, on_gesture_toggle=None, on_mic_toggle=None, on_reconnect=None):
        self.root = tk.Tk()
        self.root.title("ALFRAGANUS AI ? Autonomous Cybernetic System")
        self.root.geometry("1100x760")
        self.root.configure(bg=C_BG)

        self.on_gesture_toggle = on_gesture_toggle
        self.on_mic_toggle = on_mic_toggle
        self.on_reconnect = on_reconnect

        self.speaking = False
        self.mic_muted = False
        self.gesture_enabled = True
        
        self.latest_cv_frame = None
        self.current_preview_tk = None
        self.fs_window = None
        self.fs_canvas = None
        self.fs_preview_tk = None

        self.orb_angle = 0
        self.orb_scale = 1.0
        self.root_destroyed = False
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self._setup_ui()
        self._start_loops()

    def _on_window_close(self):
        self.root_destroyed = True
        try:
            self.root.destroy()
        except Exception:
            pass

    def _setup_ui(self):
        # 1. HEADER
        header_frame = tk.Frame(self.root, bg=C_PANEL, height=60, highlightbackground=C_BORDER, highlightthickness=1)
        header_frame.pack(fill="x", side="top", padx=10, pady=8)

        lbl_title = tk.Label(
            header_frame,
            text="?? ALFRAGANUS AI",
            font=("Segoe UI", 18, "bold"),
            fg=C_CYAN,
            bg=C_PANEL
        )
        lbl_title.pack(side="left", padx=15, pady=8)

        lbl_subtitle = tk.Label(
            header_frame,
            text="Autonomous PC Control & Neural Gesture Interface",
            font=("Segoe UI", 10),
            fg=C_GOLD,
            bg=C_PANEL
        )
        lbl_subtitle.pack(side="left", padx=5, pady=12)

        self.lbl_status = tk.Label(
            header_frame,
            text="? TIZIM TAYYOR (ONLINE)",
            font=("Segoe UI", 10, "bold"),
            fg=C_EMERALD,
            bg=C_PANEL
        )
        self.lbl_status.pack(side="right", padx=20, pady=12)

        # 2. MAIN CONTAINER
        main_container = tk.Frame(self.root, bg=C_BG)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # LEFT PANEL (Telemetry + Camera Preview)
        left_panel = tk.Frame(main_container, bg=C_PANEL, width=300, highlightbackground=C_BORDER, highlightthickness=1)
        left_panel.pack(side="left", fill="y", padx=5, pady=5)
        left_panel.pack_propagate(False)

        lbl_telemetry = tk.Label(left_panel, text="TIZIM MONITORINGI", font=("Segoe UI", 10, "bold"), fg=C_CYAN, bg=C_PANEL)
        lbl_telemetry.pack(anchor="w", padx=12, pady=10)

        self.lbl_cpu = tk.Label(left_panel, text="CPU: 0%", font=("Consolas", 10), fg=C_TEXT, bg=C_PANEL)
        self.lbl_cpu.pack(anchor="w", padx=15, pady=2)

        self.lbl_ram = tk.Label(left_panel, text="RAM: 0%", font=("Consolas", 10), fg=C_TEXT, bg=C_PANEL)
        self.lbl_ram.pack(anchor="w", padx=15, pady=2)

        self.lbl_disk = tk.Label(left_panel, text="DISK (C:): 0%", font=("Consolas", 10), fg=C_TEXT, bg=C_PANEL)
        self.lbl_disk.pack(anchor="w", padx=15, pady=2)

        self.lbl_net = tk.Label(left_panel, text="NET: ↓ 0 KB/s | ↑ 0 KB/s", font=("Consolas", 9), fg=C_CYAN, bg=C_PANEL)
        self.lbl_net.pack(anchor="w", padx=15, pady=2)

        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()

        # GESTURE CAMERA HUD BOX
        cam_header = tk.Frame(left_panel, bg=C_PANEL)
        cam_header.pack(fill="x", padx=12, pady=(14, 2))

        lbl_cam = tk.Label(cam_header, text="QO'L HARAKATLARI (LIVE HUD)", font=("Segoe UI", 9, "bold"), fg=C_GOLD, bg=C_PANEL)
        lbl_cam.pack(side="left")

        btn_fs = tk.Button(
            cam_header,
            text="⛶ Kengaytirish",
            font=("Segoe UI", 7, "bold"),
            bg="#112a45",
            fg=C_CYAN,
            relief="flat",
            padx=4,
            pady=1,
            command=self._toggle_fullscreen_camera
        )
        btn_fs.pack(side="right")

        self.lbl_gesture_state = tk.Label(left_panel, text="Holat: Faol (Ko'rsatkich barmoq)", font=("Segoe UI", 8), fg=C_MUTED, bg=C_PANEL)
        self.lbl_gesture_state.pack(anchor="w", padx=15, pady=(0, 2))

        self.cam_canvas = tk.Canvas(left_panel, width=270, height=190, bg="#02050b", highlightbackground=C_BORDER, highlightthickness=1, cursor="hand2")
        self.cam_canvas.pack(padx=12, pady=4)
        self.cam_canvas.create_text(135, 95, text="Kamera O'chiq\n(Tugmani bosing yoki ovoz bering)\nBosilsa: Katta oyna", fill=C_MUTED, font=("Segoe UI", 8), justify="center")
        self.cam_canvas.bind("<Button-1>", self._toggle_fullscreen_camera)

        # GESTURE GUIDE / CHEATSHEET
        guide_frame = tk.Frame(left_panel, bg="#060c18", highlightbackground=C_BORDER, highlightthickness=1)
        guide_frame.pack(fill="x", padx=12, pady=(4, 8))

        lbl_gtitle = tk.Label(guide_frame, text="📖 QO'L HARAKATLARI TUSHUNTIRISH", font=("Segoe UI", 8, "bold"), fg=C_CYAN, bg="#060c18")
        lbl_gtitle.pack(anchor="w", padx=8, pady=(4, 2))

        gestures_list = [
            ("☝️ 1 Barmoq", "Kursor harakati"),
            ("🤏 Pinch (Bosh+Ko'rsatkich)", "Chap chertish (Click)"),
            ("✊ Musht (Fist)", "Oynani ushlash va surish (Drag)"),
            ("✌️ 2 Barmoq", "O'ng chertish (Right Click)"),
            ("📜 Ko'rsatkich + Kichik", "Skroll qilish (Scroll)"),
            ("👐 2 Qo'l yoyish/yopish", "Kattalashtirish / Kichraytirish"),
            ("✊✊ 2 Musht", "Ish stoli (Win+D)")
        ]
        for g_icon, g_desc in gestures_list:
            row = tk.Frame(guide_frame, bg="#060c18")
            row.pack(fill="x", padx=8, pady=1)
            tk.Label(row, text=g_icon, font=("Segoe UI", 8, "bold"), fg=C_TEXT, bg="#060c18").pack(side="left")
            tk.Label(row, text=f"— {g_desc}", font=("Segoe UI", 7), fg=C_MUTED, bg="#060c18").pack(side="left", padx=3)

        # CENTER PANEL (Neural Core Visualizer)
        center_panel = tk.Frame(main_container, bg=C_PANEL, highlightbackground=C_BORDER, highlightthickness=1)
        center_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.core_canvas = tk.Canvas(center_panel, bg="#02050b", highlightthickness=0)
        self.core_canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # RIGHT PANEL (Log & Transcripts)
        right_panel = tk.Frame(main_container, bg=C_PANEL, width=320, highlightbackground=C_BORDER, highlightthickness=1)
        right_panel.pack(side="right", fill="y", padx=5, pady=5)
        right_panel.pack_propagate(False)

        lbl_log = tk.Label(right_panel, text="MULOQOT VA AMALLAR LOGI", font=("Segoe UI", 10, "bold"), fg=C_CYAN, bg=C_PANEL)
        lbl_log.pack(anchor="w", padx=12, pady=10)

        self.txt_log = tk.Text(
            right_panel,
            bg="#02050b",
            fg=C_TEXT,
            font=("Consolas", 9),
            wrap="word",
            highlightthickness=0,
            padx=8,
            pady=8
        )
        self.txt_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 3. BOTTOM CONTROL BAR
        bottom_bar = tk.Frame(self.root, bg=C_PANEL, height=55, highlightbackground=C_BORDER, highlightthickness=1)
        bottom_bar.pack(fill="x", side="bottom", padx=10, pady=8)

        self.btn_mic = tk.Button(
            bottom_bar,
            text="?? Mikrafon: YOQILGAN",
            font=("Segoe UI", 9, "bold"),
            bg="#0d2b45",
            fg=C_CYAN,
            relief="flat",
            padx=12,
            pady=6,
            command=self._toggle_mic
        )
        self.btn_mic.pack(side="left", padx=10, pady=8)

        self.btn_gesture = tk.Button(
            bottom_bar,
            text="??? Qo'l Harakatlari: FAOL",
            font=("Segoe UI", 9, "bold"),
            bg="#063826",
            fg=C_EMERALD,
            relief="flat",
            padx=12,
            pady=6,
            command=self._toggle_gesture
        )
        self.btn_gesture.pack(side="left", padx=5, pady=8)

        self.btn_recon = tk.Button(
            bottom_bar,
            text="🔄 Qayta Ulanish",
            font=("Segoe UI", 9, "bold"),
            bg="#0d2b45",
            fg=C_GOLD,
            relief="flat",
            padx=12,
            pady=6,
            command=self._reconnect_action
        )
        self.btn_recon.pack(side="left", padx=5, pady=8)

        btn_exit = tk.Button(
            bottom_bar,
            text="? Chiqish",
            font=("Segoe UI", 9, "bold"),
            bg="#3d141d",
            fg=C_RED,
            relief="flat",
            padx=15,
            pady=6,
            command=self.root.destroy
        )
        btn_exit.pack(side="right", padx=10, pady=8)

    def log(self, text: str, tag: str = "INFO"):
        if self.root_destroyed:
            return
        def _append():
            if self.root_destroyed:
                return
            try:
                timestamp = time.strftime("%H:%M:%S")
                self.txt_log.insert(tk.END, f"[{timestamp}] [{tag}] {text}\n")
                self.txt_log.see(tk.END)
            except Exception:
                pass
        try:
            self.root.after(0, _append)
        except Exception:
            pass

    def set_speaking(self, is_speaking: bool):
        self.speaking = is_speaking
        self.target_scale = 1.35 if is_speaking else 1.0

    def update_telemetry(self):
        if self.root_destroyed:
            return
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:\\').percent

            now_time = time.time()
            dt = max(0.1, now_time - getattr(self, 'last_net_time', now_time - 1.0))
            current_net = psutil.net_io_counters()

            if hasattr(self, 'last_net_io') and self.last_net_io:
                rx_rate = (current_net.bytes_recv - self.last_net_io.bytes_recv) / dt
                tx_rate = (current_net.bytes_sent - self.last_net_io.bytes_sent) / dt

                def _fmt(bytes_sec):
                    if bytes_sec > 1024 * 1024:
                        return f"{bytes_sec / (1024 * 1024):.1f} MB/s"
                    return f"{bytes_sec / 1024:.0f} KB/s"

                net_str = f"NET: ↓ {_fmt(rx_rate)} | ↑ {_fmt(tx_rate)}"
                self.lbl_net.config(text=net_str)

            self.last_net_io = current_net
            self.last_net_time = now_time

            self.lbl_cpu.config(text=f"CPU: {cpu}%")
            self.lbl_ram.config(text=f"RAM: {ram}%")
            self.lbl_disk.config(text=f"DISK (C:): {disk}%")
        except Exception:
            pass
        if not self.root_destroyed:
            try:
                self.root.after(1500, self.update_telemetry)
            except Exception:
                pass

    def update_camera_frame(self, cv_img):
        # Thread-safe image assignment without blocking
        self.latest_cv_frame = cv_img

    def _render_camera_loop(self):
        if self.root_destroyed:
            return
        if self.gesture_enabled and self.latest_cv_frame is not None:
            try:
                import cv2
                small_bgr = cv2.resize(self.latest_cv_frame, (270, 200))
                img_rgb = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                img_tk = ImageTk.PhotoImage(img_pil)
                self.current_preview_tk = img_tk
                self.cam_canvas.delete("all")
                self.cam_canvas.create_image(135, 100, image=img_tk)

                if self.fs_window is not None and self.fs_canvas is not None:
                    fw = max(100, self.fs_canvas.winfo_width())
                    fh = max(100, self.fs_canvas.winfo_height())
                    fs_bgr = cv2.resize(self.latest_cv_frame, (fw, fh))
                    fs_rgb = cv2.cvtColor(fs_bgr, cv2.COLOR_BGR2RGB)
                    fs_pil = Image.fromarray(fs_rgb)
                    fs_tk = ImageTk.PhotoImage(fs_pil)
                    self.fs_preview_tk = fs_tk
                    self.fs_canvas.delete("all")
                    self.fs_canvas.create_image(fw // 2, fh // 2, image=fs_tk)
            except Exception:
                pass
        if not self.root_destroyed:
            try:
                self.root.after(40, self._render_camera_loop)
            except Exception:
                pass

    def _toggle_fullscreen_camera(self, event=None):
        if self.fs_window is not None:
            self._close_fs_window()
            return

        self.fs_window = tk.Toplevel(self.root)
        self.fs_window.title("ALFRAGANUS LIVE CAMERA HUD (KENGAYTIRILGAN)")
        self.fs_window.geometry("850x640")
        self.fs_window.configure(bg=C_BG)
        self.fs_window.protocol("WM_DELETE_WINDOW", self._close_fs_window)

        top_bar = tk.Frame(self.fs_window, bg=C_PANEL, height=45, highlightbackground=C_BORDER, highlightthickness=1)
        top_bar.pack(fill="x", side="top", padx=10, pady=6)

        lbl = tk.Label(top_bar, text="📹 QO'L HARAKATLARI VA KAMERA LIVE HUD (KATTA OYNA)", font=("Segoe UI", 10, "bold"), fg=C_CYAN, bg=C_PANEL)
        lbl.pack(side="left", padx=12, pady=6)

        btn_close = tk.Button(top_bar, text="✕ Yopish", font=("Segoe UI", 9, "bold"), bg="#3d141d", fg=C_RED, relief="flat", padx=10, pady=2, command=self._close_fs_window)
        btn_close.pack(side="right", padx=10, pady=6)

        self.fs_canvas = tk.Canvas(self.fs_window, bg="#02050b", highlightthickness=0)
        self.fs_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _close_fs_window(self):
        if self.fs_window is not None:
            try:
                self.fs_window.destroy()
            except Exception:
                pass
            self.fs_window = None
            self.fs_canvas = None
            self.fs_preview_tk = None

    def _toggle_mic(self):
        self.mic_muted = not self.mic_muted
        if self.mic_muted:
            self.btn_mic.config(text="🎤 Mikrafon: O'CHIRILGAN", bg="#3d141d", fg=C_RED)
            self.log("Mikrafon o'chirildi.", "AUDIO")
        else:
            self.btn_mic.config(text="🎤 Mikrafon: YOQILGAN", bg="#0d2b45", fg=C_CYAN)
            self.log("Mikrafon yoqildi.", "AUDIO")

        if self.on_mic_toggle:
            self.on_mic_toggle(self.mic_muted)

    def _toggle_gesture(self):
        self.gesture_enabled = not self.gesture_enabled
        self.update_gesture_ui(self.gesture_enabled)
        if self.on_gesture_toggle:
            self.on_gesture_toggle(self.gesture_enabled)

    def update_gesture_ui(self, enabled: bool):
        self.gesture_enabled = enabled
        if enabled:
            self.btn_gesture.config(text="✋ Qo'l Harakatlari: FAOL", bg="#063826", fg=C_EMERALD)
            self.lbl_gesture_state.config(text="Holat: Faol (Kuzatilmoqda)", fg=C_EMERALD)
            self.log("Qo'l harakatlari boshqaruvi yoqildi.", "GESTURE")
        else:
            self.btn_gesture.config(text="✋ Qo'l Harakatlari: O'CHIQ", bg="#1a1c24", fg=C_MUTED)
            self.lbl_gesture_state.config(text="Holat: O'chiq", fg=C_MUTED)
            self.cam_canvas.delete("all")
            self.cam_canvas.create_text(135, 100, text="Kamera O'chiq\n(Tugmani bosing yoki ovoz bering)", fill=C_MUTED, font=("Segoe UI", 9), justify="center")
            self.latest_cv_frame = None
            self.log("Qo'l harakatlari to'xtatildi.", "GESTURE")

    def _reconnect_action(self):
        self.log("Qayta ulanish so'ralmoqda...", "SYSTEM")
        if self.on_reconnect:
            self.on_reconnect()

    def _start_loops(self):
        self.update_telemetry()
        self._animate_core()
        self._render_camera_loop()

    def _animate_core(self):
        if self.root_destroyed:
            return
        try:
            self.core_canvas.delete("all")
            w = self.core_canvas.winfo_width()
            h = self.core_canvas.winfo_height()

            if w > 10 and h > 10:
                cx, cy = w // 2, h // 2
                self.orb_angle = (self.orb_angle + 2) % 360
                self.orb_scale += (self.target_scale - self.orb_scale) * 0.1

                r_base = int(min(w, h) * 0.22 * self.orb_scale)

                color_core = C_EMERALD if self.speaking else C_CYAN
                self.core_canvas.create_oval(
                    cx - r_base, cy - r_base,
                    cx + r_base, cy + r_base,
                    outline=color_core, width=3
                )
                self.core_canvas.create_oval(
                    cx - r_base * 0.7, cy - r_base * 0.7,
                    cx + r_base * 0.7, cy + r_base * 0.7,
                    outline=C_GOLD, width=1
                )

                rad = math.radians(self.orb_angle)
                num_dots = 16
                for i in range(num_dots):
                    a = rad + (2 * math.pi / num_dots) * i
                    px = cx + int(math.cos(a) * (r_base + 30))
                    py = cy + int(math.sin(a) * (r_base + 30))
                    self.core_canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill=C_CYAN, outline="")

                status_text = "ALFRAGANUS GAPIRMOQDA..." if self.speaking else "ALFRAGANUS TINGLAMOQDA"
                self.core_canvas.create_text(
                    cx, cy,
                    text=status_text,
                    fill=C_TEXT,
                    font=("Segoe UI", 11, "bold")
                )
        except Exception:
            pass

        if not self.root_destroyed:
            try:
                self.root.after(40, self._animate_core)
            except Exception:
                pass

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("Mainloop error:", e)
