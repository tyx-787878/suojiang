# smartlock/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/recognition/', include('recognition.urls')),
    path('api-auth/', include('rest_framework.urls')),
    # 前端路由
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
]