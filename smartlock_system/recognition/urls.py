# recognition/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('face-recognition/', views.face_recognition_api, name='face-recognition'),
    path('voice-recognition/', views.voice_recognition_api, name='voice-recognition'),
    path('train-face/', views.train_face_api, name='train-face'),
    path('train-voice/', views.train_voice_api, name='train-voice'),
    path('door-status/', views.get_door_status, name='door-status'),
    path('set-door-status/', views.set_door_status, name='set-door-status'),
    path('access-logs/', views.get_access_logs, name='access-logs'),
    path('start-motion-detection/', views.start_motion_detection, name='start-motion-detection'),
    path('stop-motion-detection/', views.stop_motion_detection, name='stop-motion-detection'),
]