import cv2
import mediapipe as mp
import math
import numpy as np
from collections import deque
import threading

class FaceAnalyzer:
    def __init__(self, config):
        self.config = config
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=5,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)
        
        self.LEFT_EYE_CENTER = [33, 133, 159, 145, 153, 154]
        self.RIGHT_EYE_CENTER = [263, 362, 386, 374, 380, 381]
        self.LEFT_EYE_REGION = [33, 133, 160, 159, 158, 144]
        self.LEFT_EYE_TOP = 159
        self.LEFT_EYE_BOTTOM = 145
        self.NOSE_TIP = 1
        
        self.attention_scores = {}
        self.eye_closed_counters = {}
        self.frame_counters = {}
        self.running = False
        
    def average_point(self, landmarks, indices, w, h):
        x = sum([landmarks[i].x for i in indices]) / len(indices)
        y = sum([landmarks[i].y for i in indices]) / len(indices)
        return int(x * w), int(y * h)
    
    def get_angle(self, p1, p2):
        return math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
    
    def detect_gaze_direction(self, frame, eye_landmarks, w, h):
        x_coords = [int(landmark.x * w) for landmark in eye_landmarks]
        y_coords = [int(landmark.y * h) for landmark in eye_landmarks]
        xmin, xmax = min(x_coords), max(x_coords)
        ymin, ymax = min(y_coords), max(y_coords)

        eye_img = frame[ymin:ymax, xmin:xmax]
        if eye_img.size == 0:
            return "indéfini"

        gray = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

        M = cv2.moments(threshold)
        if M['m00'] == 0:
            return "indéfini"
        cx = int(M['m10'] / M['m00'])
        pos = cx / (xmax - xmin)

        if pos < 0.35:
            return "gauche"
        elif pos > 0.65:
            return "droite"
        else:
            return "centre"
    
    def is_eye_closed(self, landmarks, top_idx, bottom_idx, w, h, threshold=None):
        if threshold is None:
            threshold = self.config.EYE_CLOSED_THRESHOLD
        top_y = int(landmarks[top_idx].y * h)
        bottom_y = int(landmarks[bottom_idx].y * h)
        distance = abs(bottom_y - top_y)
        return distance < threshold
    
    def analyze_faces(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            success, frame = cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.face_mesh.process(rgb)
            h, w, _ = frame.shape

            current_scores = {}
            
            if result.multi_face_landmarks:
                for face_id, face_landmarks in enumerate(result.multi_face_landmarks):
                    if face_id not in self.attention_scores:
                        self.attention_scores[face_id] = deque(maxlen=self.config.ATTENTION_HISTORY_SIZE)
                        self.eye_closed_counters[face_id] = 0
                        self.frame_counters[face_id] = 0
                    
                    x_coords = [int(lm.x * w) for lm in face_landmarks.landmark]
                    y_coords = [int(lm.y * h) for lm in face_landmarks.landmark]
                    xmin, xmax = min(x_coords), max(x_coords)
                    ymin, ymax = min(y_coords), max(y_coords)

                    left_eye = self.average_point(face_landmarks.landmark, self.LEFT_EYE_CENTER, w, h)
                    right_eye = self.average_point(face_landmarks.landmark, self.RIGHT_EYE_CENTER, w, h)
                    nose = int(face_landmarks.landmark[self.NOSE_TIP].x * w), int(face_landmarks.landmark[self.NOSE_TIP].y * h)

                    angle = self.get_angle(left_eye, right_eye)
                    eye_points = [face_landmarks.landmark[i] for i in self.LEFT_EYE_REGION]
                    gaze = self.detect_gaze_direction(frame, eye_points, w, h)
                    eye_closed = self.is_eye_closed(face_landmarks.landmark, self.LEFT_EYE_TOP, self.LEFT_EYE_BOTTOM, w, h)

                    if eye_closed:
                        self.eye_closed_counters[face_id] += 1
                        self.attention_scores[face_id].append(0)
                    else:
                        self.eye_closed_counters[face_id] = 0
                        if abs(angle) > 15 or gaze != "centre":
                            self.attention_scores[face_id].append(0)
                        else:
                            self.attention_scores[face_id].append(1)

                    if len(self.attention_scores[face_id]) > 0:
                        current_score = sum(self.attention_scores[face_id]) / len(self.attention_scores[face_id]) * 100
                        current_scores[face_id] = current_score

            if current_scores:
                avg_score = sum(current_scores.values()) / len(current_scores)
                with open(self.config.ATTENTION_DATA_FILE, "w") as f:
                    f.write(f"{avg_score:.1f}")
                    for face_id, score in current_scores.items():
                        f.write(f"\nface_{face_id}:{score:.1f}")

        cap.release()
    
    def start(self):
        self.running = True
        self.analysis_thread = threading.Thread(target=self.analyze_faces, daemon=True)
        self.analysis_thread.start()
    
    def stop(self):
        self.running = False
        if hasattr(self, 'analysis_thread'):
            self.analysis_thread.join()
        self.face_mesh.close()