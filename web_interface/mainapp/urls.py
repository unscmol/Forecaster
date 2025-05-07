from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # 导入本模块中的 views.py
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),  # 使用内置登录视图
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
]