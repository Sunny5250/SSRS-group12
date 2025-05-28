# Django URL配置模块导入
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView  # Django内置的登录登出视图

# 本地视图导入
from . import views

# 应用命名空间，用于URL反向解析
app_name = 'accounts'

# URL模式列表
urlpatterns = [
    # 登录页面
    # 使用Django内置的LoginView处理登录请求
    # template_name指定登录页面模板
    path('login/', 
         LoginView.as_view(template_name='accounts/login.html'), 
         name='login'),
    
    # 登出处理
    # 使用Django内置的LogoutView处理登出请求
    # 登出后默认重定向到首页
    path('logout/', 
         LogoutView.as_view(), 
         name='logout'),
    
    # 用户注册页面
    # 使用自定义的RegisterView处理注册请求
    # 注册成功后自动登录并跳转到自习室列表
    path('register/', 
         views.RegisterView.as_view(), 
         name='register'),
    
    # 用户资料页面
    # 使用自定义的ProfileView处理个人资料查看和更新
    # 需要用户登录才能访问
    path('profile/', 
         views.ProfileView.as_view(), 
         name='profile'),
]
