# utils/face_recognition.py
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime


class FaceRecognition:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()

    def load_known_faces(self):
        # 加载已知人脸数据
        known_faces_dir = "data/known_faces"
        for person_name in os.listdir(known_faces_dir):
            person_dir = os.path.join(known_faces_dir, person_name)
            if os.path.isdir(person_dir):
                for image_name in os.listdir(person_dir):
                    image_path = os.path.join(person_dir, image_name)
                    image = face_recognition.load_image_file(image_path)
                    face_encoding = face_recognition.face_encodings(image)[0]
                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(person_name)

    def recognize_faces(self, frame):
        # 将图像从BGR颜色（OpenCV使用）转换为RGB颜色（face_recognition使用）
        rgb_frame = frame[:, :, ::-1]

        # 找到当前帧中的所有人脸位置和人脸编码
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # 查看该人脸是否与已知人脸匹配
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # 如果有匹配项，使用已知人脸中距离最近的一个
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
                confidence = round((1 - face_distances[best_match_index]) * 100, 2)
                name = f"{name} ({confidence}%)"

            face_names.append(name)

        return face_locations, face_names

    def detect_emotion(self, frame, face_locations):
        # 简化的情绪识别实现
        emotions = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 加载预训练的情绪识别模型（这里使用简化版本）
        emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

        for (top, right, bottom, left) in face_locations:
            face_roi = gray[top:bottom, left:right]
            # 在实际应用中，这里应该使用深度学习模型进行情绪预测
            # 简化处理，随机返回一种情绪（实际应用中需要使用训练好的模型）
            emotion_index = np.random.randint(0, 7)
            emotions.append(emotion_dict[emotion_index])

        return emotions

    def save_face(self, frame, face_location, person_name):
        # 保存新的人脸数据
        top, right, bottom, left = face_location
        face_image = frame[top:bottom, left:right]

        # 创建用户目录
        person_dir = os.path.join("data/known_faces", person_name)
        os.makedirs(person_dir, exist_ok=True)

        # 保存人脸图像
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(person_dir, f"{timestamp}.jpg")
        cv2.imwrite(image_path, face_image)

        # 更新已知人脸数据
        self.load_known_faces()

        return image_path