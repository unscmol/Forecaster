from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # 导入本模块中的 views.py
urlpatterns = [
    path('login/', views.user_login, name='login'),  # 使用内置登录视图
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('', views.home, name='home'),  # 主页
    path('create/', views.create_job, name='create_job'),  # 创建作业页面
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),  # 作业详情页
]