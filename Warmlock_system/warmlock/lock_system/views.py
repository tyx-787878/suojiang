from django.http import HttpResponse

def register(request):
    return HttpResponse("注册页面测试成功！")

def home(request):
    return HttpResponse("首页测试成功！")