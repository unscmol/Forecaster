import os, glob, shutil
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseForbidden, Http404
from urllib.parse import unquote as urlunquote
from django.db.models import Case, When, IntegerField

import subprocess
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
import ast  # 新增导入
from .models import Job, UserRanking


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
    task_type = request.GET.get("task_type", "1")
    sort = request.GET.get("sort", "job_id")
    order = request.GET.get("order", "asc")

    # 合法排序字段列表
    valid_sort_fields = ['job_id', 'task_type', 'status']
    if sort not in valid_sort_fields:
        sort = 'job_id'
    if order not in ['asc', 'desc']:
        order = 'asc'

    # 排序顺序前缀
    order_prefix = '' if order == 'asc' else '-'

    # 排序：Favored 优先，再按指定字段排序
    jobs = Job.objects.filter(user=request.user).order_by(
        Case(
            When(status='Favored', then=0),
            When(status='Pending', then=1),
            When(status='Finishing', then=2),
            default=3,
            output_field=IntegerField()
        ),
        f"{order_prefix}{sort}"
    )

    # 排行榜（按分数高低）
    rankings = UserRanking.objects.select_related('user', 'best_job').filter(
        task_type=task_type
    ).order_by("-best_score")

    return render(request, 'mainapp/home.html', {
        'jobs': jobs,
        'rankings': rankings,
        'task_type': task_type,
        'sort': sort,
        'order': order,
    })

@login_required
def create_job(request):
    if request.method == 'POST':
        user = request.user
        task_type = request.POST.get('task_type')
        extra_params_str = request.POST.get('extra_params', '').strip()

        # 创建 Job 并保存数据库
        job = Job(user=user, task_type=task_type, status="Pending")
        job.save()
        job_id = job.job_id

        # === 读取默认参数 ===
        default_config_path = os.path.join(
            main_path,
            'config', 'system_config', 'task_default_config',
            f'task{int(task_type)}.json'
        )

        if not os.path.exists(default_config_path):
            raise FileNotFoundError(f"默认配置文件不存在: {default_config_path}")

        with open(default_config_path, 'r') as f:
            job_params = json.load(f)

        # === 合并 extra_params（若有）===
        try:
            user_params = json.loads(extra_params_str) if extra_params_str else {}
            if not isinstance(user_params, dict):
                raise ValueError("extra_params 不是合法字典")
        except Exception as e:
            return render(request, 'mainapp/create_job.html', {
                'error_message': f"额外参数格式错误：{str(e)}"
            })

        # 覆盖默认配置中的值
        job_params.update(user_params)

        # === 填充系统必须参数 ===
        job_params['user_id'] = user.username
        job_params['task_id'] = int(task_type)
        job_params['job_number'] = job_id

        # === 保存到 job_config ===
        job_params_filename = f"job_params_{user.username}_{job_id}.json"
        job_params_path = os.path.join(main_path, 'config', 'job_config', job_params_filename)

        os.makedirs(os.path.dirname(job_params_path), exist_ok=True)
        with open(job_params_path, 'w') as json_file:
            json.dump(job_params, json_file, indent=4)

        # === 执行准备数据脚本 ===
        prepare_script_path = os.path.join(main_path, 'scripts', 'prepare_data.py')
        if os.path.exists(job_params_path):
            subprocess.run(['python', prepare_script_path, job_params_path])
        else:
            print(f"[数据准备失败] 找不到文件: {job_params_path}")

        return redirect('job_detail', job_id=job_id)

    return render(request, 'mainapp/create_job.html')

@login_required
def job_detail(request, job_id): # 跳转作业细节页面
    job = Job.objects.get(job_id=job_id)  # 获取作业对象
    return render(request, 'mainapp/job_detail.html', {'job': job})


@login_required
def submit_evaluation(request, job_id):
    job = get_object_or_404(Job, job_id=job_id)
    username = job.user.username
    job_number = job.job_id

    params_filename = f"job_params_{username}_{job_number}.json"
    params_path = os.path.join(main_path, 'config', 'job_config', params_filename)

    evaluate_path = os.path.join(main_path, 'scripts', 'task_evaluate.py')
    postprocess_path = os.path.join(main_path, 'scripts', 'task_post_process.py')

    log_dir = os.path.join(main_path, 'misc', 'log')
    download_dir = os.path.join(main_path, 'interactive_space', username, 'download_data')
    os.makedirs(download_dir, exist_ok=True)

    log_eval = f"task_evaluate_{username}_jobid{job_number}.log"
    log_post = f"task_post_process_{username}_jobid{job_number}.log"
    log_eval_path = os.path.join(log_dir, log_eval)
    log_post_path = os.path.join(log_dir, log_post)

    success = True
    rank_score = None

    if os.path.exists(params_path):
        try:
            subprocess.run(['python', evaluate_path, params_path], check=True)
        except subprocess.CalledProcessError as e:
            success = False
            print(f"[评估脚本失败] {e}")

        if success:
            try:
                subprocess.run(['python', postprocess_path, params_path], check=True)
                # ✅ 从缓存目录中读取 rank_score
                score_file_path = os.path.join(main_path, 'data', 'temp', 'cached_data',
                                               f'rank_score_jobid_{job_number}.txt')
                if os.path.exists(score_file_path):
                    with open(score_file_path, 'r') as f:
                        rank_score = float(f.read().strip())
                else:
                    success = False
                    print(f"[后处理失败] 找不到得分文件: {score_file_path}")
            except subprocess.CalledProcessError as e:
                success = False
                print(f"[后处理脚本失败] {e}")
    else:
        success = False
        print(f"[评估失败] 找不到参数文件: {params_path}")

    if rank_score is None:
        print("没有读取到RANK_SCORE:，无法更新job信息！")

    if success and job.status != "Favored":
        if rank_score is not None:
            print(f"===> Writing rank_score={rank_score} to job {job.job_id}")
            job.rank_score = rank_score
        job.status = "Finishing"
        job.save()

        # 更新排行榜
        from .models import UserRanking
        if rank_score is not None:
            UserRanking.objects.update_or_create(
                user=job.user,
                task_type=job.task_type,
                defaults={
                    'best_score': rank_score,
                    'best_job': job,
                }
            )
    else:
        for log_file in [log_eval_path, log_post_path]:
            if os.path.exists(log_file):
                shutil.copy(log_file, download_dir)

    return redirect('job_detail', job_id=job_id)





@login_required
def finish_job(request, job_id): #结束任务
    job = get_object_or_404(Job, job_id=job_id)
    if request.method == 'POST':
        job.status = 'Finishing'
        job.save()
        return redirect('home')
    return redirect('job_detail', job_id=job_id)


@login_required
def cloud_disk(request, username):
    if request.user.username != username:
        return HttpResponseForbidden("你无权访问该用户的云盘")

    subpath = urlunquote(request.GET.get('path', '').strip('/'))
    user_root = os.path.join(main_path, 'interactive_space', username)
    current_path = os.path.join(user_root, subpath)

    if not os.path.commonpath([os.path.abspath(current_path), user_root]) == os.path.abspath(user_root):
        return HttpResponseForbidden("非法路径访问")

    os.makedirs(current_path, exist_ok=True)

    if request.method == "POST":
        # ✅ 上传文件
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            save_path = os.path.join(current_path, uploaded_file.name)
            with open(save_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            return redirect(f"{request.path}?path={subpath}")

        # ✅ 删除文件或文件夹
        if 'delete_file' in request.POST:
            target = request.POST.get('delete_file')
            target_path = os.path.join(current_path, target)
            if os.path.exists(target_path):
                if os.path.isfile(target_path):
                    os.remove(target_path)
                elif os.path.isdir(target_path):
                    shutil.rmtree(target_path)
            return redirect(f"{request.path}?path={subpath}")

        # ✅ 新建文件夹
        if 'new_folder' in request.POST:
            folder_name = request.POST.get('new_folder_name', '').strip()
            if folder_name:
                folder_path = os.path.join(current_path, folder_name)
                os.makedirs(folder_path, exist_ok=True)
            return redirect(f"{request.path}?path={subpath}")

    # 浏览文件
    file_list = []
    for name in os.listdir(current_path):
        path = os.path.join(current_path, name)
        file_list.append({
            'name': name,
            'size': os.path.getsize(path) if os.path.isfile(path) else '-',
            'is_file': os.path.isfile(path),
            'is_dir': os.path.isdir(path),
        })

    parent_path = os.path.dirname(subpath) if subpath else ''

    return render(request, 'mainapp/cloud_disk.html', {
        'username': username,
        'subpath': subpath,
        'parent_path': parent_path,
        'files': file_list,
    })

@login_required
def download_file(request, username, filename):
    subpath = request.GET.get('path', '').strip('/')
    user_root = os.path.join(main_path, 'interactive_space', username)
    file_path = os.path.join(user_root, subpath, filename)

    if request.user.username != username:
        return HttpResponseForbidden("禁止访问他人文件")
    if not os.path.exists(file_path):
        raise Http404("文件不存在")

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)



@login_required
def rankings(request):
    task_type = request.GET.get("task_type", "1")
    rankings = UserRanking.objects.select_related('best_job').filter(task_type=task_type).order_by("-best_score")
    return render(request, 'mainapp/rankings.html', {
        'rankings': rankings,
        'task_type': task_type
    })




@login_required
def mark_favored(request, job_id):
    job = get_object_or_404(Job, job_id=job_id, user=request.user)
    job.status = "Favored"
    job.save()
    return redirect('job_detail', job_id=job_id)


@login_required
def unmark_favored(request, job_id):
    job = get_object_or_404(Job, job_id=job_id, user=request.user)

    if job.status == "Favored":
        job.status = "Finishing"
        job.save()

    return redirect('job_detail', job_id=job_id)


@login_required
def organize_jobs(request):
    if request.method == "POST":
        finishing_jobs = Job.objects.filter(user=request.user, status="Finishing")
        username = request.user.username
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Forecaster根目录

        for job in finishing_jobs:
            job_id = job.job_id

            # 删除文件夹1: config/job_config/*
            pattern1 = os.path.join(base, 'config', 'job_config', f'*_{job_id}.*')
            for path in glob.glob(pattern1):
                os.remove(path)

            # 删除文件夹2: data/user_data/<user>/download_data/*
            pattern2 = os.path.join(base, 'data', 'user_data', username, 'download_data', f'*_{job_id}.*')
            for path in glob.glob(pattern2):
                os.remove(path)

            # 删除文件夹3: data/user_data/<user>/upload_data/*
            pattern3 = os.path.join(base, 'data', 'user_data', username, 'upload_data', f'*_{job_id}.*')
            for path in glob.glob(pattern3):
                os.remove(path)

            # 删除文件夹4: data/user_data/<user>/test_job_data/job_id/
            folder4 = os.path.join(base, 'data', 'user_data', username, 'test_job_data', str(job_id))
            if os.path.exists(folder4):
                shutil.rmtree(folder4)

            # 删除文件夹5: interactive_space/<user>/download_data/*
            pattern5 = os.path.join(base, 'interactive_space', username, 'download_data', f'*_{job_id}.*')
            for path in glob.glob(pattern5):
                os.remove(path)

            # 最后从数据库中删除 Job 对象
            job.delete()

    return redirect('home')







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