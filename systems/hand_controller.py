# systems/hand_controller.py
import cv2
import mediapipe as mp
import threading


class HandController:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Datos para cada mano por lateralidad
        self.hands_data = {
            "Left":  {"x": screen_w // 3,       "y": screen_h // 2, "gesture": "none", "detected": False},
            "Right": {"x": screen_w * 2 // 3,   "y": screen_h // 2, "gesture": "none", "detected": False},
        }

        self.lock = threading.Lock()

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,          # detectamos hasta 2 manos
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

        self.cap     = cv2.VideoCapture(0)
        self.running = False
        self.thread  = None
        self.debug_frame = None

    def start(self):
        self.running = True
        self.thread  = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print("Cámara iniciada.")

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        print("Cámara detenida.")

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame     = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results   = self.hands.process(rgb_frame)

            with self.lock:
                # Reseteamos detección de ambas manos
                for side in self.hands_data:
                    self.hands_data[side]["detected"] = False
                    self.hands_data[side]["gesture"]  = "none"

                if results.multi_hand_landmarks and results.multi_handedness:
                    for hand_landmarks, handedness in zip(
                        results.multi_hand_landmarks,
                        results.multi_handedness
                    ):
                        # MediaPipe devuelve "Left" o "Right"
                        # Como el frame está espejado, los lados están invertidos
                        raw_side = handedness.classification[0].label
                        side = "Right" if raw_side == "Left" else "Left"

                        landmarks = hand_landmarks.landmark
                        self._process_landmarks(landmarks, frame.shape, side)
                        self._draw_debug(frame, hand_landmarks, side)

                self.debug_frame = frame

    def _process_landmarks(self, landmarks, frame_shape, side):
        wrist = landmarks[0]
        palm  = landmarks[9]
        raw_x = (wrist.x + palm.x) / 2
        raw_y = (wrist.y + palm.y) / 2

        self.hands_data[side]["x"]        = int(raw_x * self.screen_w)
        self.hands_data[side]["y"]        = int(raw_y * self.screen_h)
        self.hands_data[side]["detected"] = True
        self.hands_data[side]["gesture"]  = self._detect_gesture(landmarks)

    def _finger_is_up(self, landmarks, tip_id, pip_id):
        return landmarks[tip_id].y < landmarks[pip_id].y

    def _detect_gesture(self, landmarks):
        index_up  = self._finger_is_up(landmarks, 8,  6)
        middle_up = self._finger_is_up(landmarks, 12, 10)
        ring_up   = self._finger_is_up(landmarks, 16, 14)
        pinky_up  = self._finger_is_up(landmarks, 20, 18)
        fingers_up = sum([index_up, middle_up, ring_up, pinky_up])

        if fingers_up == 0:
            return "fist"
        elif fingers_up >= 3:
            return "open"
        elif index_up and not middle_up:
            return "point"
        else:
            return "none"

    def _draw_debug(self, frame, hand_landmarks, side):
        mp_drawing = mp.solutions.drawing_utils
        # Color diferente por jugador: cyan para izquierda, magenta para derecha
        color = (0, 255, 200) if side == "Left" else (255, 0, 180)
        mp_drawing.draw_landmarks(
            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
            mp_drawing.DrawingSpec(color=color, thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=color, thickness=2),
        )

    def get_state(self, side="Left"):
        """Retorna el estado de una mano específica."""
        with self.lock:
            return dict(self.hands_data[side])

    def get_both_states(self):
        """Retorna el estado de ambas manos."""
        with self.lock:
            return {
                "Left":  dict(self.hands_data["Left"]),
                "Right": dict(self.hands_data["Right"]),
            }

    def get_debug_frame(self):
        with self.lock:
            return self.debug_frame