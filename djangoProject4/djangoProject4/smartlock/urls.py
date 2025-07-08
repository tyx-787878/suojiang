from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 将recognition应用的URL包含进来，访问路径以/api/recognition/开头
    path('api/recognition/', include('recognition.urls')),
]


