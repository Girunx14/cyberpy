import cv2
import mediapipe as mp
import threading


class HandController:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.hand_x = screen_w // 2
        self.hand_y = screen_h // 2
        self.gesture = "none"
        self.hand_detected = False
        self.lock = threading.Lock()

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.cap = cv2.VideoCapture(1)
        self.running = False
        self.thread = None
        self.debug_frame = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
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
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            with self.lock:
                if results.multi_hand_landmarks:
                    self.hand_detected = True
                    landmarks = results.multi_hand_landmarks[0].landmark
                    self._process_landmarks(landmarks, frame.shape)
                    self._draw_debug(frame, results.multi_hand_landmarks[0])
                else:
                    self.hand_detected = False
                    self.gesture = "none"
                self.debug_frame = frame

    def _process_landmarks(self, landmarks, frame_shape):
        wrist = landmarks[0]
        palm  = landmarks[9]
        raw_x = (wrist.x + palm.x) / 2
        raw_y = (wrist.y + palm.y) / 2
        self.hand_x = int(raw_x * self.screen_w)
        self.hand_y = int(raw_y * self.screen_h)
        self.gesture = self._detect_gesture(landmarks)

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

    def _draw_debug(self, frame, hand_landmarks):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def get_state(self):
        with self.lock:
            return {
                "x":        self.hand_x,
                "y":        self.hand_y,
                "gesture":  self.gesture,
                "detected": self.hand_detected,
            }

    def get_debug_frame(self):
        with self.lock:
            return self.debug_frame