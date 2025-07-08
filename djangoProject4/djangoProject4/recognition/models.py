# recognition/models.py
from django.db import models
from django.contrib.auth.models import User


class FaceData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='face_data/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FaceData for {self.user.username}"


class VoiceData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio = models.FileField(upload_to='voice_data/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"VoiceData for {self.user.username}"


class AccessLog(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('FACE', '人脸识别'),
        ('VOICE', '声纹识别'),
        ('PASSWORD', '密码'),
        ('MANUAL', '手动'),
    ]

    RESULT_CHOICES = [
        ('SUCCESS', '成功'),
        ('FAILURE', '失败'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_access_type_display()} - {self.get_result_display()} at {self.timestamp}"


class DoorStatus(models.Model):
    STATUS_CHOICES = [
        ('OPEN', '开启'),
        ('CLOSED', '关闭'),
        ('LOCKED', '锁定'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CLOSED')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Door is {self.get_status_display()} (updated at {self.last_updated})"