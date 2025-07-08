# recognition/views.py
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import FaceData, VoiceData, AccessLog, DoorStatus
from .utils import FaceRecognition, VoiceRecognition, MotionDetection
import cv2
import json
import base64
import numpy as np
from django.core.files.base import ContentFile

# 初始化识别器
face_recognizer = FaceRecognition()
voice_recognizer = VoiceRecognition()
motion_detector = MotionDetection()


@csrf_exempt
@login_required
def face_recognition_api(request):
    if request.method == 'POST':
        try:
            # 获取图像数据
            data = json.loads(request.body)
            image_data = data.get('image')

            if not image_data:
                return JsonResponse({'error': 'No image provided'}, status=400)

            # 解码base64图像
            img_data = base64.b64decode(image_data.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # 执行人脸识别
            face_locations, face_names = face_recognizer.recognize_faces(frame)

            # 检测情绪
            emotions = face_recognizer.detect_emotion(frame, face_locations)

            # 记录访问日志
            if face_names and face_names[0] != "Unknown":
                username = face_names[0].split(' ')[0]
                try:
                    user = User.objects.get(username=username)
                    AccessLog.objects.create(
                        user=user,
                        access_type='FACE',
                        result='SUCCESS',
                        details=f"Emotion: {emotions[0] if emotions else 'None'}"
                    )
                    # 如果识别成功，自动开门
                    door_status, created = DoorStatus.objects.get_or_create(id=1)
                    door_status.status = 'OPEN'
                    door_status.save()
                except User.DoesNotExist:
                    pass

            return JsonResponse({
                'face_locations': face_locations,
                'face_names': face_names,
                'emotions': emotions
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def voice_recognition_api(request):
    if request.method == 'POST':
        try:
            # 获取音频数据
            audio_file = request.FILES.get('audio')

            if not audio_file:
                return JsonResponse({'error': 'No audio provided'}, status=400)

            # 保存临时音频文件
            temp_file = f"temp_audio_{request.user.id}.wav"
            with open(temp_file, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            # 执行声纹识别
            recognized_name, confidence = voice_recognizer.recognize_voice(temp_file)

            # 记录访问日志
            if recognized_name != "Unknown":
                try:
                    user = User.objects.get(username=recognized_name)
                    AccessLog.objects.create(
                        user=user,
                        access_type='VOICE',
                        result='SUCCESS',
                        details=f"Confidence: {confidence:.2f}"
                    )
                    # 如果识别成功，自动开门
                    door_status, created = DoorStatus.objects.get_or_create(id=1)
                    door_status.status = 'OPEN'
                    door_status.save()
                except User.DoesNotExist:
                    pass

            # 删除临时文件
            os.remove(temp_file)

            return JsonResponse({
                'recognized_name': recognized_name,
                'confidence': float(confidence)
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def train_face_api(request):
    if request.method == 'POST':
        try:
            # 获取图像数据和用户名
            data = json.loads(request.body)
            image_data = data.get('image')
            username = data.get('username')

            if not image_data or not username:
                return JsonResponse({'error': 'Missing image or username'}, status=400)

            # 解码base64图像
            img_data = base64.b64decode(image_data.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # 检测人脸
            face_locations, _ = face_recognizer.recognize_faces(frame)

            if not face_locations:
                return JsonResponse({'error': 'No face detected'}, status=400)

            # 保存人脸数据
            face_location = face_locations[0]  # 只处理第一张脸
            image_path = face_recognizer.save_face(frame, face_location, username)

            # 保存到数据库
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # 如果用户不存在，创建新用户
                user = User.objects.create_user(username=username, password='default_password')

            face_data = FaceData(user=user, image=image_path)
            face_data.save()

            return JsonResponse({'success': True, 'message': 'Face trained successfully'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def train_voice_api(request):
    if request.method == 'POST':
        try:
            # 获取音频数据和用户名
            audio_file = request.FILES.get('audio')
            username = request.POST.get('username')

            if not audio_file or not username:
                return JsonResponse({'error': 'Missing audio or username'}, status=400)

            # 保存临时音频文件
            temp_file = f"temp_audio_{request.user.id}.wav"
            with open(temp_file, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            # 训练声纹
            voice_path = voice_recognizer.save_voice(temp_file, username)

            # 保存到数据库
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # 如果用户不存在，创建新用户
                user = User.objects.create_user(username=username, password='default_password')

            voice_data = VoiceData(user=user, audio=voice_path)
            voice_data.save()

            # 删除临时文件
            os.remove(temp_file)

            return JsonResponse({'success': True, 'message': 'Voice trained successfully'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def get_door_status(request):
    try:
        status = DoorStatus.objects.last() or DoorStatus.objects.create()
        return JsonResponse({
            'status': status.status,
            'last_updated': status.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def set_door_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')

            if new_status not in [choice[0] for choice in DoorStatus.STATUS_CHOICES]:
                return JsonResponse({'error': 'Invalid status'}, status=400)

            status, created = DoorStatus.objects.get_or_create(id=1)
            status.status = new_status
            status.save()

            # 记录操作日志
            AccessLog.objects.create(
                user=request.user,
                access_type='MANUAL',
                result='SUCCESS',
                details=f"Door status set to {new_status}"
            )

            return JsonResponse({'success': True, 'status': status.status})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def get_access_logs(request):
    try:
        logs = AccessLog.objects.all().order_by('-timestamp')[:50]
        log_data = []

        for log in logs:
            log_data.append({
                'user': log.user.username if log.user else 'Unknown',
                'access_type': log.get_access_type_display(),
                'result': log.get_result_display(),
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'details': log.details
            })

        return JsonResponse({'logs': log_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def start_motion_detection(request):
    try:
        if not motion_detector.is_detecting:
            # 在单独的线程中运行运动检测
            import threading
            thread = threading.Thread(target=motion_detector.start_detection)
            thread.daemon = True
            thread.start()

        return JsonResponse({'success': True, 'message': 'Motion detection started'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def stop_motion_detection(request):
    try:
        if motion_detector.is_detecting:
            motion_detector.stop_detection()

        return JsonResponse({'success': True, 'message': 'Motion detection stopped'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)