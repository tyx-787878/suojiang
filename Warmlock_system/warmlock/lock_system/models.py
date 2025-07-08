from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    face_data = models.BinaryField(null=True)  # 存储人脸特征
    voice_data = models.BinaryField(null=True)  # 存储语音特征
    unlock_phrase = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    access_time = models.DateTimeField(auto_now_add=True)
    access_type = models.CharField(max_length=10)  # 'face', 'voice', 'both'
    is_successful = models.BooleanField()
    face_match_score = models.FloatField(null=True)
    voice_match_score = models.FloatField(null=True)
    image_path = models.CharField(max_length=255, null=True)
    audio_path = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.user} - {self.access_time}"