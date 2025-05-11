import os
import sys
import json
import datetime
import traceback

'''
由于web端调用的子进程，脚本的根目录默认是web_interface，若要回到Forecaster，需要回退！！！
'''

# ✅ 设置 Django 项目根路径并初始化环境（确保能导入 models）
#引入自定义函数
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
web_root = os.path.join(project_root, 'web_interface')
sys.path.append(web_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_interface.settings")

# ✅ 添加自定义函数路径（用于 Task_Processor）
sys.path.append(os.path.join(project_root, 'src', 'untils'))
sys.path.append(os.path.join(project_root, 'src', 'model_evaluator'))

import django
django.setup()

import django
django.setup()

# ✅ 导入 Django 模型
from django.contrib.auth.models import User
from mainapp.models import UserRanking
from post_process_src import Task_Processor




# ✅ 获取参数文件路径
job_params_file = sys.argv[1]

with open(job_params_file, "r") as f:
    job_params = json.load(f)

username = job_params["user_id"]
job_number = job_params["job_number"]

# ✅ 构造日志输出路径
log_dir = os.path.join(project_root, "misc", "log")
os.makedirs(log_dir, exist_ok=True)
log_filename = f"task_post_process_{username}_jobid{job_number}.log"
log_path = os.path.join(log_dir, log_filename)

sys.stdout = open(log_path, 'w', encoding='utf-8')
sys.stderr = sys.stdout

print(f"[{datetime.datetime.now()}] 开始评估任务 user_id={username}, job_id={job_number}")
print(f"使用参数文件: {job_params_file}")

try:
    Post_Task = Task_Processor(
        job_params,
        username,
        job_params['task_id'],
        job_number
    )
    rank_score = Post_Task.execute_process()
    print(f"[{datetime.datetime.now()}] 评估完成 ✅")
    print("Rank Score is {}".format(rank_score))

    # ✅ 更新排行榜
    user = User.objects.get(username=username)
    entry, created = UserRanking.objects.get_or_create(user=user, task_type=job_params["task_id"])
    entry.best_score = max(entry.best_score, rank_score)
    entry.save()
    print(f"[{datetime.datetime.now()}] 排行榜已更新 ✅")

except Exception as e:
    print(f"[{datetime.datetime.now()}] 评估失败 ❌: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

finally:
    sys.stdout.flush()
    sys.stdout.close()