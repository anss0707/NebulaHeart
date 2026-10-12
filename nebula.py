# ==============================================================================
# 🌌 TECHNICAL NOTES & DOCUMENTATION: NEBULAHEART 3D (SPACE GESTURE CONTROLLER)
# ==============================================================================
#
# 📝 ALUR EKSEKUSI TERMINAL (CHEAT SHEET):
# ------------------------------------------------------------------------------
# 1. Matikan venv lokal yang aktif saat ini:
#    $ deactivate
#
# 2. Aktifkan lingkungan conda yang sudah lengkap library-nya:
#    $ conda activate space_gesture
#
# 3. Jalankan kodenya:
#    $ python index.py  (atau python nebula.py)
# ------------------------------------------------------------------------------
#
# 📝 DESKRIPSI PROYEK:
# Sebuah aplikasi interaktif visualisasi 3D real-time yang mengontrol gerakan 
# dan formasi 1.500 partikel kosmis menggunakan kecerdasan buatan (AI) pelacak 
# tangan berbasis visi komputer.
#
# ⚙️ TEKNOLOGI UTAMA (TECH STACK):
# 1. Python 3.11    - Bahasa pemrograman utama (Sangat stabil untuk proyek ini).
# 2. Pygame         - Mengatur jendela aplikasi, frame-rate (60 FPS), dan input keyboard.
# 3. PyOpenGL       - Akses kartu grafis (GPU) untuk render 3D partikel secara real-time.
# 4. MediaPipe      - AI buatan Google untuk mendeteksi 21 titik koordinat kerangka tangan.
# 5. OpenCV (cv2)   - Mengakses webcam, memproses frame video, dan menampilkan monitor kamera.
# 6. NumPy 1.26.4   - Komputasi matriks kilat untuk kalkulasi posisi rumus matematika 3D.
#
# 🎛️ PANDUAN KONTROL GESTUR TANGAN (MAPPED GESTURES):
# ------------------------------------------------------------------------------
# | JARI TANGAN          | MODE | NAMA MODE             | EFEK VISUAL PARTIKEL |
# ------------------------------------------------------------------------------
# | Terbuka Lebar        |  1   | ROTASI ANGCOSMOS      | Partikel biru acak   |
# |                      |      |                       | berputar lambat.     |
# |                      |      |                       |                      |
# | 1 Jari Telunjuk Tegak|  2   | SATURNUS 3D           | Mengumpul jadi bola  |
# | (Jari lain menekuk)  |      |                       | oranye & cincin emas.|
# |                      |      |                       |                      |
# | 2 Jari (Peace Sign)  |  3   | TEKS I LOVE YOU       | Berbaris membentuk   |
# |                      |      |                       | tulisan biru neon.   |
# |                      |      |                       |                      |
# | Kepal/Genggam Tangan |  4   | BENTUK HATI (LOVE)    | Mengalir membentuk   |
# |                      |      |                       | ikon hati pink tajam.|
# ------------------------------------------------------------------------------
#
# 🛠️ CARA SETUP DI KOMPUTER BARU / LAPTOP LAIN:
# 1. Unduh & Instal Miniconda (Versi Python 3.11) serta VS Code.
# 2. Buka Terminal, buat lingkungan virtual baru:
#    $ conda create -n space_gesture python=3.11 -y
# 3. Aktifkan lingkungan baru tersebut:
#    $ conda activate space_gesture
# 4. Instal semua library (Wajib versi numpy 1.26.4 agar tidak crash dengan OpenGL):
#    $ pip install opencv-python mediapipe pygame PyOpenGL numpy==1.26.4
#
# 🚀 CATATAN JALANKAN DI macOS:
# Jika aplikasi langsung freeze/menutup sendiri karena aturan Main Thread GUI Mac,
# gunakan perintah 'pythonw' (bukan python atau python3):
#    $ pythonw index.py
#
# ==============================================================================

import sys
import math
import time
import numpy as np
import cv2
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE, K_q, K_1, K_2, K_3, K_4, K_SPACE

try:
    from OpenGL.GL import (
        glClear, glClearColor, glEnable, glDisable, glBlendFunc,
        glPointSize, glBegin, glEnd, glVertex3f, glColor4f,
        glMatrixMode, glLoadIdentity, glTranslatef, glRotatef,
        GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST,
        GL_BLEND, GL_SRC_ALPHA, GL_ONE, GL_ONE_MINUS_SRC_ALPHA,
        GL_POINT_SMOOTH, GL_PROJECTION, GL_MODELVIEW, GL_POINTS
    )
    from OpenGL.GLU import gluPerspective
except ImportError:
    print("[ERROR] PyOpenGL is not installed. Please install PyOpenGL.")
    sys.exit(1)

try:
    import mediapipe as mp
except ImportError:
    mp = None
    print("[WARNING] MediaPipe is not installed. Running in keyboard fallback mode.")

# --- CONSTANTS ---
NUM_PARTICLES = 1500
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
TARGET_FPS = 60

MODE_ANGCOSMOS = 1
MODE_SATURN = 2
MODE_TEXT = 3
MODE_HEART = 4

MODE_NAMES = {
    MODE_ANGCOSMOS: "ROTASI ANGCOSMOS",
    MODE_SATURN: "SATURNUS 3D",
    MODE_TEXT: "TEKS I LOVE YOU",
    MODE_HEART: "BENTUK HATI (LOVE)"
}


class ParticleSystem:
    """Manages 1,500 3D cosmic particles, formations, morphing transitions, and rendering."""

    def __init__(self, count=NUM_PARTICLES):
        self.count = count
        self.positions = np.zeros((count, 3), dtype=np.float32)
        self.target_positions = np.zeros((count, 3), dtype=np.float32)
        self.colors = np.zeros((count, 4), dtype=np.float32)
        self.target_colors = np.zeros((count, 4), dtype=np.float32)
        self.lerp_speed = 0.07

        # Pre-generate target shape data
        self.cosmos_pos, self.cosmos_col = self._generate_cosmos()
        self.saturn_pos, self.saturn_col = self._generate_saturn()
        self.text_pos, self.text_col = self._generate_text("I LOVE YOU")
        self.heart_pos, self.heart_col = self._generate_heart()

        # Initialize to Angcosmos
        self.current_mode = MODE_ANGCOSMOS
        self.positions[:] = self.cosmos_pos
        self.target_positions[:] = self.cosmos_pos
        self.colors[:] = self.cosmos_col
        self.target_colors[:] = self.cosmos_col

    def _generate_cosmos(self):
        """Mode 1: Angcosmos - Spherical cosmic cloud with spiral arm distribution and cosmic blue shades."""
        pos = np.zeros((self.count, 3), dtype=np.float32)
        cols = np.zeros((self.count, 4), dtype=np.float32)

        for i in range(self.count):
            # Spiral cosmic nebula distribution
            theta = np.random.uniform(0, 4 * np.pi)
            radius = np.random.uniform(0.5, 3.8) + np.random.normal(0, 0.25)
            height = np.random.normal(0, 0.7) * (1.0 - radius / 4.5)
            
            # 2 spiral arms
            arm_offset = (i % 2) * np.pi
            x = radius * np.cos(theta + arm_offset) * 0.75
            y = height
            z = radius * np.sin(theta + arm_offset) * 0.75
            pos[i] = [x, y, z]

            # Colors: Deep cosmic blue, cyan, electric blue
            palette_choice = np.random.rand()
            if palette_choice < 0.6:
                # Electric / cyan blue
                cols[i] = [0.1, np.random.uniform(0.6, 0.95), 1.0, np.random.uniform(0.7, 0.95)]
            elif palette_choice < 0.85:
                # Deep cosmos indigo blue
                cols[i] = [0.15, 0.35, np.random.uniform(0.85, 1.0), np.random.uniform(0.6, 0.85)]
            else:
                # Sparkling bright white-blue star
                cols[i] = [0.85, 0.95, 1.0, 1.0]

        return pos, cols

    def _generate_saturn(self):
        """Mode 2: Saturnus 3D - Orange spherical core & tilted golden rings."""
        pos = np.zeros((self.count, 3), dtype=np.float32)
        cols = np.zeros((self.count, 4), dtype=np.float32)

        # 600 particles for spherical planet core, 900 for golden rings
        num_planet = 600
        num_ring = self.count - num_planet

        # 1. Planet Sphere (Orange / Amber)
        planet_radius = 1.35
        for i in range(num_planet):
            phi = np.random.uniform(0, 2 * np.pi)
            costheta = np.random.uniform(-1, 1)
            u = np.random.uniform(0.85, 1.0)
            r = planet_radius * (u ** (1 / 3))
            theta = np.arccos(costheta)
            
            x = r * np.sin(theta) * np.cos(phi)
            y = r * np.sin(theta) * np.sin(phi)
            z = r * np.cos(theta)
            pos[i] = [x, y, z]

            # Warm amber & glowing orange colors
            r_col = np.random.uniform(0.95, 1.0)
            g_col = np.random.uniform(0.42, 0.65)
            b_col = np.random.uniform(0.05, 0.2)
            cols[i] = [r_col, g_col, b_col, np.random.uniform(0.75, 0.95)]

        # 2. Golden Rings (Flat annular disk tilted at ~26 degrees)
        r_inner = 1.85
        r_outer = 3.65
        tilt_angle = math.radians(26.0)

        for i in range(num_ring):
            idx = num_planet + i
            # Annular ring radius
            r = np.sqrt(np.random.uniform(r_inner ** 2, r_outer ** 2))
            angle = np.random.uniform(0, 2 * np.pi)
            thickness = np.random.normal(0, 0.04)

            # Flat ring in XZ plane
            xr = r * np.cos(angle)
            yr = thickness
            zr = r * np.sin(angle)

            # Tilt ring around X axis
            y_tilted = yr * math.cos(tilt_angle) - zr * math.sin(tilt_angle)
            z_tilted = yr * math.sin(tilt_angle) + zr * math.cos(tilt_angle)

            pos[idx] = [xr, y_tilted, z_tilted]

            # Colors: Shimmering gold and amber rings
            gold_tone = np.random.rand()
            if gold_tone < 0.7:
                # Vibrant gold
                cols[idx] = [1.0, np.random.uniform(0.82, 0.95), np.random.uniform(0.2, 0.35), np.random.uniform(0.8, 1.0)]
            else:
                # Pale bright gold
                cols[idx] = [1.0, 0.92, np.random.uniform(0.5, 0.75), np.random.uniform(0.85, 1.0)]

        return pos, cols

    def _generate_text(self, text="I LOVE YOU"):
        """Mode 3: Teks I LOVE YOU - Neon blue glowing letters in 3D space."""
        pos = np.zeros((self.count, 3), dtype=np.float32)
        cols = np.zeros((self.count, 4), dtype=np.float32)

        # Render text to an offscreen Pygame surface and extract coordinates
        pygame.font.init()
        font_size = 90
        # Try finding standard font
        font = None
        for font_name in ["arial", "dejavusans", "helvetica", "liberationsans", "freesans"]:
            try:
                font = pygame.font.SysFont(font_name, font_size, bold=True)
                if font:
                    break
            except Exception:
                continue
        if font is None:
            font = pygame.font.Font(None, font_size)

        text_surface = font.render(text, True, (255, 255, 255))
        w, h = text_surface.get_size()
        arr = pygame.surfarray.array2d(text_surface)
        pixel_coords = np.argwhere(arr > 0)

        if len(pixel_coords) == 0:
            # Fallback simple line coordinates if font render fails
            pixel_coords = np.column_stack([np.linspace(0, 100, 500), np.zeros(500)])

        # Sample exactly self.count coordinates with replacement if needed
        indices = np.random.choice(len(pixel_coords), size=self.count, replace=True)
        sampled = pixel_coords[indices].astype(np.float32)

        # Center and normalize coordinates to 3D space
        center_x = w / 2.0
        center_y = h / 2.0
        scale = 6.2 / max(w, 1)

        x_coords = (sampled[:, 0] - center_x) * scale
        # Invert Y so text isn't upside-down
        y_coords = (center_y - sampled[:, 1]) * scale
        z_coords = np.random.normal(0, 0.12, size=self.count).astype(np.float32)

        pos[:, 0] = x_coords
        pos[:, 1] = y_coords
        pos[:, 2] = z_coords

        # Colors: Neon electric blue glow
        for i in range(self.count):
            blue_variant = np.random.rand()
            if blue_variant < 0.7:
                # Neon electric cyan-blue
                cols[i] = [0.0, np.random.uniform(0.85, 1.0), 1.0, np.random.uniform(0.8, 1.0)]
            else:
                # Bright neon blue with white highlight
                cols[i] = [np.random.uniform(0.4, 0.7), np.random.uniform(0.9, 1.0), 1.0, 1.0]

        return pos, cols

    def _generate_heart(self):
        """Mode 4: 3D Parametric Heart - Sharp vivid pink/magenta pulsating heart."""
        pos = np.zeros((self.count, 3), dtype=np.float32)
        cols = np.zeros((self.count, 4), dtype=np.float32)

        for i in range(self.count):
            t = np.random.uniform(-np.pi, np.pi)
            # Parametric 2D heart boundary
            xh = 16.0 * (np.sin(t) ** 3)
            yh = 13.0 * np.cos(t) - 5.0 * np.cos(2 * t) - 2.0 * np.cos(3 * t) - np.cos(4 * t)
            
            # Fill interior volume with radial jitter
            fill_factor = np.sqrt(np.random.uniform(0.05, 1.0))
            x = xh * fill_factor * 0.18
            y = yh * fill_factor * 0.18

            # Z depth profile: thicker in middle, sharper at edges
            r_from_center = math.sqrt((x * 1.5) ** 2 + y ** 2)
            max_depth = max(0.05, 1.2 - r_from_center * 0.35)
            z = np.random.uniform(-max_depth, max_depth) * 0.65

            pos[i] = [x, y, z]

            # Colors: Vivid sharp hot pink / magenta
            pink_var = np.random.rand()
            if pink_var < 0.75:
                # Vivid hot pink / magenta
                cols[i] = [1.0, np.random.uniform(0.1, 0.28), np.random.uniform(0.65, 0.88), np.random.uniform(0.8, 1.0)]
            else:
                # Deep glowing crimson-pink
                cols[i] = [1.0, 0.05, np.random.uniform(0.4, 0.55), np.random.uniform(0.75, 0.95)]

        return pos, cols

    def set_mode(self, mode):
        """Transition particles smoothly to the specified mode."""
        if mode == self.current_mode:
            return
        self.current_mode = mode

        if mode == MODE_ANGCOSMOS:
            self.target_positions[:] = self.cosmos_pos
            self.target_colors[:] = self.cosmos_col
        elif mode == MODE_SATURN:
            self.target_positions[:] = self.saturn_pos
            self.target_colors[:] = self.saturn_col
        elif mode == MODE_TEXT:
            self.target_positions[:] = self.text_pos
            self.target_colors[:] = self.text_col
        elif mode == MODE_HEART:
            self.target_positions[:] = self.heart_pos
            self.target_colors[:] = self.heart_col

    def update(self, delta_time, total_time):
        """Morph positions and colors toward target smoothly, with organic turbulence."""
        # Smooth interpolation (lerp)
        self.positions += (self.target_positions - self.positions) * self.lerp_speed
        self.colors += (self.target_colors - self.colors) * self.lerp_speed

        # Mode-specific dynamics
        if self.current_mode == MODE_HEART:
            # Rhythmic heartbeat pulsation
            pulse = 1.0 + 0.07 * math.sin(total_time * 6.0) + 0.03 * math.sin(total_time * 12.0)
            self.positions[:] = (self.target_positions * pulse - self.positions) * self.lerp_speed + self.positions
        elif self.current_mode == MODE_ANGCOSMOS:
            # Subtle cosmic drift / turbulence
            noise = np.sin(total_time * 1.5 + self.positions[:, 0]) * 0.003
            self.positions[:, 1] += noise

    def render(self):
        """Draw 1,500 particles using PyOpenGL."""
        glBegin(GL_POINTS)
        for i in range(self.count):
            c = self.colors[i]
            p = self.positions[i]
            glColor4f(float(c[0]), float(c[1]), float(c[2]), float(c[3]))
            glVertex3f(float(p[0]), float(p[1]), float(p[2]))
        glEnd()


class HandGestureTracker:
    """Handles webcam input, MediaPipe hand landmark detection, and gesture recognition."""

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.is_camera_open = False
        self.mp_hands = None
        self.hands = None
        self.mp_draw = None

        # Gesture detection state
        self.detected_mode = MODE_ANGCOSMOS
        self.gesture_name = "Terbuka Lebar (Angcosmos)"
        self.history = []
        self.history_len = 5
        self.hand_center = (0.5, 0.5)
        self.is_hand_present = False

        self._init_camera()
        self._init_mediapipe()

    def _init_camera(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if self.cap.isOpened():
                self.is_camera_open = True
                print(f"[INFO] Webcam successfully opened on index {self.camera_index}.")
            else:
                print(f"[WARNING] Webcam index {self.camera_index} could not be opened. Running in fallback mode.")
        except Exception as e:
            print(f"[ERROR] Exception opening webcam: {e}")

    def _init_mediapipe(self):
        if mp is not None:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.65,
                min_tracking_confidence=0.55
            )
            self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self):
        """Captures frame, detects landmarks, classifies gestures, and displays monitor window."""
        if not self.is_camera_open or self.cap is None:
            return None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None

        # Mirror frame horizontally for intuitive interaction
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.is_hand_present = False
        raw_mode = None

        if self.hands is not None:
            results = self.hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                self.is_hand_present = True
                hand_landmarks = results.multi_hand_landmarks[0]

                # Draw landmarks on frame
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=3),
                    self.mp_draw.DrawingSpec(color=(255, 0, 128), thickness=2, circle_radius=2)
                )

                # Classify fingers & gesture
                raw_mode, gesture_text = self._classify_gesture(hand_landmarks.landmark)

                # Track hand center (palm wrist / middle knuckle average)
                wrist = hand_landmarks.landmark[0]
                middle_mcp = hand_landmarks.landmark[9]
                self.hand_center = ((wrist.x + middle_mcp.x) * 0.5, (wrist.y + middle_mcp.y) * 0.5)

                # Stabilize gesture with rolling voting buffer
                if raw_mode is not None:
                    self.history.append(raw_mode)
                    if len(self.history) > self.history_len:
                        self.history.pop(0)

                    # Majority vote
                    voted_mode = max(set(self.history), key=self.history.count)
                    self.detected_mode = voted_mode
                    self.gesture_name = gesture_text

        # Annotate webcam feed with HUD info
        self._draw_hud(frame)

        # Show OpenCV monitor window
        cv2.imshow("NEBULAHEART 3D - Camera Tracking", frame)
        cv2.waitKey(1)

        return self.detected_mode

    def _classify_gesture(self, landmarks):
        """
        Classifies hand gesture into 1 of the 4 defined modes:
        1. Open Hand (Terbuka Lebar) -> MODE_ANGCOSMOS (1)
        2. Pointing Index Finger (1 Jari Telunjuk Tegak) -> MODE_SATURN (2)
        3. Peace Sign / 2 Fingers (2 Jari) -> MODE_TEXT (3)
        4. Fist (Kepal / Genggam Tangan) -> MODE_HEART (4)
        """
        wrist = landmarks[0]

        def dist(p1, p2):
            return math.hypot(p1.x - p2.x, p1.y - p2.y)

        # Finger tip vs pip distance relative to wrist
        # Index: 8 (tip), 6 (pip)
        # Middle: 12 (tip), 10 (pip)
        # Ring: 16 (tip), 14 (pip)
        # Pinky: 20 (tip), 18 (pip)
        index_up = dist(landmarks[8], wrist) > dist(landmarks[6], wrist) * 1.15 and landmarks[8].y < landmarks[6].y
        middle_up = dist(landmarks[12], wrist) > dist(landmarks[10], wrist) * 1.15 and landmarks[12].y < landmarks[10].y
        ring_up = dist(landmarks[16], wrist) > dist(landmarks[14], wrist) * 1.15 and landmarks[16].y < landmarks[14].y
        pinky_up = dist(landmarks[20], wrist) > dist(landmarks[18], wrist) * 1.15 and landmarks[20].y < landmarks[18].y
        thumb_up = dist(landmarks[4], landmarks[2]) > dist(landmarks[3], landmarks[2]) * 1.25

        up_fingers_count = sum([index_up, middle_up, ring_up, pinky_up])

        # Classification logic:
        # Mode 4: Fist (Genggam) -> All 4 main fingers folded
        if not index_up and not middle_up and not ring_up and not pinky_up:
            return MODE_HEART, "Kepalan Tangan (Bentuk Hati)"

        # Mode 2: 1 Jari Telunjuk Tegak -> Index only
        if index_up and not middle_up and not ring_up and not pinky_up:
            return MODE_SATURN, "1 Telunjuk Tegak (Saturnus 3D)"

        # Mode 3: 2 Jari (Peace Sign) -> Index and Middle up, Ring & Pinky folded
        if index_up and middle_up and not ring_up and not pinky_up:
            return MODE_TEXT, "2 Jari Peace (Teks I LOVE YOU)"

        # Mode 1: Terbuka Lebar -> 3 or more fingers up (Open hand)
        if up_fingers_count >= 3:
            return MODE_ANGCOSMOS, "Terbuka Lebar (Rotasi Angcosmos)"

        return self.detected_mode, self.gesture_name

    def _draw_hud(self, frame):
        """Draw aesthetic status HUD on webcam monitor."""
        h, w, _ = frame.shape
        # Top banner background
        cv2.rectangle(frame, (0, 0), (w, 75), (20, 20, 24), -1)
        cv2.line(frame, (0, 75), (w, 75), (0, 255, 200), 2)

        # Title
        cv2.putText(frame, "NEBULAHEART 3D CONTROLLER", (15, 26),
                    cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 1)

        # Active Mode badge
        mode_str = f"MODE {self.detected_mode}: {MODE_NAMES.get(self.detected_mode, 'UNKNOWN')}"
        mode_colors = {
            MODE_ANGCOSMOS: (255, 200, 0),  # Blue/Cyan
            MODE_SATURN: (0, 165, 255),      # Orange
            MODE_TEXT: (255, 255, 0),        # Cyan/Blue
            MODE_HEART: (180, 50, 255)       # Pink/Magenta
        }
        color = mode_colors.get(self.detected_mode, (0, 255, 0))
        cv2.putText(frame, mode_str, (15, 58),
                    cv2.FONT_HERSHEY_DUPLEX, 0.72, color, 2)

        # Bottom info bar
        cv2.rectangle(frame, (0, h - 35), (w, h), (15, 15, 18), -1)
        help_text = "Tangan: " + self.gesture_name + " | [1-4] Manual Key | [Q] Quit"
        cv2.putText(frame, help_text, (15, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    def release(self):
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()


class NebulaApp:
    """Main Application Controller: Pygame + PyOpenGL 3D Scene + Event Loop."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("NEBULAHEART 3D (SPACE GESTURE CONTROLLER)")
        
        # Setup PyOpenGL context
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
        self.clock = pygame.time.Clock()

        # Initialize OpenGL scene
        self._init_opengl()

        # Components
        self.particles = ParticleSystem(NUM_PARTICLES)
        self.tracker = HandGestureTracker(camera_index=0)

        # View rotation angles
        self.rot_x = 15.0
        self.rot_y = 0.0
        self.rot_z = 0.0
        self.auto_rotate = True
        self.running = True

    def _init_opengl(self):
        """Configure OpenGL projection, depth test, alpha blending, and point smoothing."""
        glClearColor(0.02, 0.02, 0.04, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for luminous cosmic glow
        glEnable(GL_POINT_SMOOTH)
        glPointSize(3.5)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, (WINDOW_WIDTH / WINDOW_HEIGHT), 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def run(self):
        """Main application execution loop (60 FPS)."""
        print("[INFO] Application running. Press '1'-'4' to switch modes manually, 'Q' or ESC to exit.")
        start_time = time.time()
        last_time = time.time()

        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            total_time = current_time - start_time

            # 1. Handle Pygame Events
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key in (K_ESCAPE, K_q):
                        self.running = False
                    elif event.key == K_1:
                        self.particles.set_mode(MODE_ANGCOSMOS)
                    elif event.key == K_2:
                        self.particles.set_mode(MODE_SATURN)
                    elif event.key == K_3:
                        self.particles.set_mode(MODE_TEXT)
                    elif event.key == K_4:
                        self.particles.set_mode(MODE_HEART)
                    elif event.key == K_SPACE:
                        self.auto_rotate = not self.auto_rotate

            # 2. Process Hand Gesture from Webcam
            detected_mode = self.tracker.process_frame()
            if detected_mode is not None:
                self.particles.set_mode(detected_mode)

            # 3. Handle 3D Scene Rotation (Gesture influenced + Continuous Cosmic Drift)
            if self.tracker.is_hand_present:
                # Interactive tilt based on hand position
                hx, hy = self.tracker.hand_center
                target_rot_y = (hx - 0.5) * 120.0
                target_rot_x = (hy - 0.5) * 80.0
                self.rot_y += (target_rot_y - self.rot_y) * 0.05
                self.rot_x += (target_rot_x - self.rot_x) * 0.05
            elif self.auto_rotate:
                # Slow cosmic orbit rotation
                self.rot_y += 0.45

            # 4. Update Particle Physics & Formations
            self.particles.update(dt, total_time)

            # 5. Render OpenGL Frame
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            # Position camera
            glTranslatef(0.0, 0.0, -8.2)
            glRotatef(self.rot_x, 1.0, 0.0, 0.0)
            glRotatef(self.rot_y, 0.0, 1.0, 0.0)
            glRotatef(self.rot_z, 0.0, 0.0, 1.0)

            # Render 1,500 particles
            self.particles.render()

            pygame.display.flip()
            self.clock.tick(TARGET_FPS)

        # Cleanup
        self.tracker.release()
        pygame.quit()
        print("[INFO] NEBULAHEART 3D closed gracefully.")


if __name__ == "__main__":
    app = NebulaApp()
    app.run()
