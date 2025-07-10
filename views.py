import base64
from datetime import datetime
from .models import RecognitionLog
from django.shortcuts import render, redirect
from deepface import DeepFace
import cv2
import os
import numpy as np
from PIL import Image
from io import BytesIO
import torch
from modelscope.pipelines import pipeline
from django.http import JsonResponse
# from modelscope.preprocessors import AudioBrainPreprocessor

import librosa
import soundfile as sf

import logging

logger = logging.getLogger(__name__)  # 获取当前模块日志器

#  # 保存原始的torch.load函数
original_torch_load = torch.load

os.environ['NO_PROXY'] = 'www.modelscope.cn'

def face_recognition(request):
    logger.info("进入人脸识别视图")

    if request.method == 'GET':
        logger.debug("GET 请求，用于展示摄像头页面")
        return render(request, 'lockapp/camera.html')

    elif request.method == 'POST':
        logger.info("收到 POST 请求，准备处理图片数据")
        image_data = request.POST.get("image_data")

        if not image_data:
            logger.warning("未接收到图像数据")
            return render(request, 'lockapp/fail.html', {'message': '没有图像数据'})

        try:
            logger.info("图像成功处理，开始人脸识别")
        except Exception as e:
            logger.error("识别出错: %s", str(e), exc_info=True)

        return render(request, 'lockapp/face_result.html')

FAMILY_PHOTOS = {
    "潇潇": "known_faces/xiao.jpg",
}

recognition_history = []

face_model = DeepFace.build_model("Facenet")


def index(request):
    return render(request, 'lockapp/index.html')

def camera(request):
    return render(request, 'lockapp/camera.html')

def face_recognition(request):
    global detected_emotion
    if request.method == "POST":
        image_data = request.POST.get("image_data")
        if not image_data:
            return render(request, 'lockapp/fail.html', {'message': '没有收到图像数据'})

        header, encoded = image_data.split(",", 1)
        decoded = base64.b64decode(encoded)
        img = Image.open(BytesIO(decoded)).convert('RGB')
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        image_data = request.POST.get("image_data")
        if not image_data:
            print("没收到 image_data")
            return render(request, 'lockapp/fail.html', {'message': '没有收到图像数据'})

        # 保存为临时文件
        input_img_path = "input_face.jpg"
        cv2.imwrite(input_img_path, img_bgr)


        matched_name = None
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        for name, known_img in FAMILY_PHOTOS.items():
            known_img_path = os.path.join(BASE_DIR, known_img)
            if not os.path.exists(known_img_path):
                print(f"文件不存在：{known_img_path}")
                continue

            try:
                analysis = DeepFace.analyze(img_path=input_img_path, actions=['emotion'], enforce_detection=False)
                detected_emotion = analysis[0]['dominant_emotion']
            except Exception as e:
                print(f"情绪分析失败: {e}")

            try:
                result = DeepFace.verify(
                    img1_path=input_img_path,
                    img2_path=known_img_path,
                    enforce_detection=False
                )
                if result["verified"]:
                    matched_name = name
                    break
            except Exception as e:
                print(f"识别失败: {e}")
                continue

        os.remove(input_img_path)

        RecognitionLog.objects.create(
            name=matched_name if matched_name else None,
            success=bool(matched_name),
            emotion=detected_emotion
        )

        logs = RecognitionLog.objects.order_by('-timestamp')[:10]

        return render(request, 'lockapp/face_result.html', {
            'matched': bool(matched_name),
            'name': matched_name,
            'emotion': detected_emotion,
            'logs': logs
        })

    return redirect('index')


# def voice_result(request):
#     result = voice_recognition(request)
#     return render(request, 'lockapp/voice_result.html', {
#         'matched': request.GET.get('matched'),
#         'name': request.GET.get('name')
#     })


# # 重新定义torch.load，调用原始函数并强制设置weights_only=False
def safe_torch_load(*args, **kwargs):
#     # 强制覆盖weights_only参数为False（如果有传入则替换，否则添加）
    kwargs['weights_only'] = False
    print("safe_torch_load调")
    return original_torch_load(*args, **kwargs)

def voice_recognition(request):
    if request.method == "POST":
        try:
            audio_file = request.FILES.get("audio")
            temp_path = os.path.join(os.path.dirname(__file__),'temp',"temp_user_audio.wav")
            print("start")
            with open(temp_path, 'wb+') as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
            print("end")
            print("pre")
            # y, sr = librosa.load(temp_path, sr=16000, mono=True)
            # sf.write(temp_path, y, 16000, subtype='PCM_16')
            print("endpre")
    #替换torch.load为自定义函数
            print("调用模型")

            torch.load = safe_torch_load
            sv_pipline = pipeline(
                task='speaker-verification',
                model='iic/speech_rdino_ecapa_tdnn_sv_zh-cn_3dspeaker_16k',
                model_revision='v1.0.1',
            )
            print("结束调用")
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            #speaker1_a_wav = os.path.join(BASE_DIR, 'voice', 'wo.wav')
            speaker1_a_wav = os.path.join(BASE_DIR, 'voice', 'speaker1_a_cn_16k.wav')
    # # 相同说话人语音
            print("开始比较")
            print("temp_path"+temp_path)
            print("speaker1_a_wav"+speaker1_a_wav)
            result = sv_pipline([speaker1_a_wav, speaker1_a_wav])
            print("endsv")
            # result = {'score': 1.0, 'text': 'yes'}
            similarity = result['score']  # 获取相似度分数
            print("结束比较")
            print(result)
    # 4. 根据阈值判断是否匹配（阈值可调整，0.7是常见值）
            matched = similarity > 0.7
            os.remove(temp_path)  # 删除临时文件

            return JsonResponse({
                'status': 'success',
                'matched': matched,
                'username': '我' if matched else None,
                'similarity': float(similarity),  # 返回相似度供调试
                'message': f'识别成功: {str()}'
            })

        except Exception as e:
            print("e"+str(e))
            return JsonResponse({
                'status': 'error',
                'message': f'识别失败: {str(e)}'
            }, status=500)
    # # # 不同说话人语音
    # result = sv_pipline([speaker1_a_wav, speaker2_a_wav])
    # print(result)
    # # # 可以自定义得分阈值来进行识别
    # result = sv_pipline([speaker1_a_wav, speaker2_a_wav], thr=0.198)
    # print(result)
    return render(request,'lockapp/voice_recognition.html')
