from django.urls import path
from . import views

urlpatterns = [
    # 假设要创建一个获取用户列表的API接口，路径为/users/
    path('users/', views.user_list, name='user-list'),
]