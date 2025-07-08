INSTALLED_APPS = [
    # ...
    'rest_framework',
    'corsheaders',
    'recognition',
    'accounts',
    'devices',
]

# 添加媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS设置
CORS_ALLOW_ALL_ORIGINS = True

# REST framework设置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}