from django.urls import path
from . import views
from .views import index, face_recognition, voice_recognition

urlpatterns = [
    path('', views.index, name='index'),
    path('camera/', views.camera, name='camera'),
    path('face/',views.face_recognition,name='face_recognition'),
    path('voice/',views.voice_recognition,name='voice_recognition'),
]
