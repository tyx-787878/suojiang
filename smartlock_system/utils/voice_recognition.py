# utils/voice_recognition.py
import speech_recognition as sr
import librosa
import numpy as np
import os
from scipy.io import wavfile
import pickle


class VoiceRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.known_voices = {}
        self.load_known_voices()

    def load_known_voices(self):
        # 加载已知声纹数据
        voices_dir = "data/known_voices"
        if os.path.exists(voices_dir) and os.listdir(voices_dir):
            for voice_file in os.listdir(voices_dir):
                if voice_file.endswith(".pkl"):
                    person_name = os.path.splitext(voice_file)[0]
                    voice_path = os.path.join(voices_dir, voice_file)
                    with open(voice_path, 'rb') as f:
                        voice_features = pickle.load(f)
                        self.known_voices[person_name] = voice_features

    def extract_features(self, audio_file):
        # 提取音频特征
        y, sr = librosa.load(audio_file, sr=16000)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return np.mean(mfccs, axis=1)

    def recognize_voice(self, audio_file):
        # 声纹识别
        features = self.extract_features(audio_file)
        min_distance = float('inf')
        recognized_name = "Unknown"

        for person_name, known_features in self.known_voices.items():
            distance = np.linalg.norm(features - known_features)
            if distance < min_distance:
                min_distance = distance
                recognized_name = person_name

        # 设置相似度阈值
        if min_distance > 30:  # 阈值需要根据实际情况调整
            recognized_name = "Unknown"

        return recognized_name, min_distance

    def save_voice(self, audio_file, person_name):
        # 保存新的声纹数据
        features = self.extract_features(audio_file)

        # 创建用户目录
        voices_dir = "data/known_voices"
        os.makedirs(voices_dir, exist_ok=True)

        # 保存声纹特征
        voice_path = os.path.join(voices_dir, f"{person_name}.pkl")
        with open(voice_path, 'wb') as f:
            pickle.dump(features, f)

        # 更新已知声纹数据
        self.load_known_voices()

        return voice_path

    def listen_for_command(self):
        # 监听语音命令
        with sr.Microphone() as source:
            print("请说出指令...")
            audio = self.recognizer.listen(source)

        try:
            # 使用Google Speech Recognition识别语音
            text = self.recognizer.recognize_google(audio, language='zh-CN')
            print(f"识别结果: {text}")
            return text
        except sr.UnknownValueError:
            print("无法识别语音")
            return None
        except sr.RequestError as e:
            print(f"请求错误; {e}")
            return None