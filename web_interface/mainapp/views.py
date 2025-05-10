import os
import json


from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import subprocess
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
import ast  # 新增导入

main_path = 'C:\\Users\ZY\Desktop\Forecaster'


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # 保存用户
            create_user_dirs(user.username, main_path)  # 注册成功后创建目录
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'mainapp/register.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # 获取用户对象
            login(request, user)  # 登录
            return redirect('home')  # 登录成功后跳转
        else:
            return render(request, 'registration/login.html', {'form': form, 'error': '登录失败，请检查用户名和密码'})
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

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


# mainapp/views.py
from .models import Job

@login_required
def home(request):
    jobs = Job.objects.filter(user=request.user)  # 获取当前用户的所有作业
    return render(request, 'mainapp/home.html', {'jobs': jobs})

@login_required
def create_job(request):
    if request.method == 'POST':
        # 获取用户ID和任务类型
        user = request.user  # 当前登录的用户
        task_type = request.POST.get('task_type')  # 从表单获取任务类型

        # 创建新的作业对象（job_id 会自动生成）
        job = Job(user=user, task_type=task_type, status="Pending")
        job.save()  # 保存到数据库，这里 job_id 会自动递增

        # 获取 job_id
        job_id = job.job_id

        # 创建 job 参数字典
        job_params = {
            "total_data_path": "../data/processed/archive_data/dataset_1/total_data_dic.joblib",
            "user_id": user.username,  # 用户名
            "task_id": int(task_type),  # 任务类型1
            "job_number": job_id,  # 使用数据库自动生成的 job_id
            "inp_len": 16,
            "out_len": 16,
            "step_len": 1,
            "Custom_evaluation": 0
        }

        # 设置存储路径
        job_params_filename = f"job_params_{user.username}_{job_id}.json"
        job_params_path = os.path.join(main_path, 'config', 'job_config', job_params_filename)

        # 保存参数字典为 JSON 文件
        with open(job_params_path, 'w') as json_file:
            json.dump(job_params, json_file, indent=4)

        # 运行 prepare_data.py，传递配置文件路径
        cmd = f"python {os.path.join(main_path, 'scripts', 'prepare_data.py')} {job_params_path}"
        subprocess.Popen(cmd, shell=True)

        # 重定向到作业详情页
        return redirect('job_detail', job_id=job_id)  # 跳转到作业详情页

    return render(request, 'mainapp/create_job.html')

@login_required
def job_detail(request, job_id):
    job = Job.objects.get(job_id=job_id)  # 获取作业对象
    return render(request, 'mainapp/job_detail.html', {'job': job})

def user_logout(request):
    logout(request)  # 登出操作
    return redirect('login')  # 登出后重定向到登录页面




'''
辅助函数
'''

def create_user_dirs(username, main_path):
    # 创建 data/user_data/username 目录结构
    data_user_path = os.path.join(main_path, 'data', 'user_data', username)
    os.makedirs(os.path.join(data_user_path, 'download_data'), exist_ok=True)
    os.makedirs(os.path.join(data_user_path, 'test_job_data'), exist_ok=True)
    os.makedirs(os.path.join(data_user_path, 'upload_data'), exist_ok=True)

    # 创建 interactive_space/username 目录结构
    inter_user_path = os.path.join(main_path, 'interactive_space', username)
    os.makedirs(os.path.join(inter_user_path, 'download_data'), exist_ok=True)
    os.makedirs(os.path.join(inter_user_path, 'upload_data'), exist_ok=True)