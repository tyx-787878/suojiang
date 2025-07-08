from django.http import JsonResponse

def user_list(request):
    # 这里只是示例，实际可能从数据库获取用户列表
    users = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
    return JsonResponse(users, safe=False)