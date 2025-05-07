from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import subprocess
from django.contrib.auth.forms import UserCreationForm


def register(request):
    if request.method == 'POST':
        # 使用 Django 内置的 UserCreationForm 来处理注册
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # 保存用户
            return redirect('login')  # 注册成功后跳转到登录页面
    else:
        form = UserCreationForm()  # GET 请求时创建一个空表单
    return render(request, 'mainapp/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'mainapp/login.html', {'error': '登录失败，请检查用户名密码'})
    return render(request, 'mainapp/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    return render(request, 'mainapp/home.html')

@login_required
def execute_cmd(request):
    result = ''
    if request.method == 'POST':
        cmd = request.POST.get('command', '')
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            result = e.output
    return render(request, 'mainapp/home.html', {'result': result})



def register(request):
    if request.method == 'POST':
        # 使用 Django 内置的 UserCreationForm 来处理注册
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # 保存用户
            return redirect('login')  # 注册成功后跳转到登录页面
    else:
        form = UserCreationForm()  # GET 请求时创建一个空表单
    return render(request, 'mainapp/register.html', {'form': form})