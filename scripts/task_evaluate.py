import os
import sys
import json
import numpy as np
import pandas as pd
import pickle
import shutil
import matplotlib.pyplot as plt
import joblib
import datetime

#引入自定义函数
sys.path.append(r"..\src\untils")
sys.path.append(r"..\src\model_evaluator")
from forecaster_fuction import check_missing_values, split_train_test_data_by_time
from evaluate_src import Task_Evaluator

# 获取传入的参数文件路径
job_params_file = sys.argv[1]  # 命令行参数：超参数 JSON 文件路径

# 读取超参数
with open(job_params_file, "r") as f:
    job_params = json.load(f)

# 提取用户和任务标识
username = job_params["user_id"]
job_number = job_params["job_number"]

# 构造日志目录和文件名
log_dir = os.path.abspath(os.path.join("..", "misc", "log"))
os.makedirs(log_dir, exist_ok=True)

log_filename = f"task_evaluate_{username}_jobid{job_number}.log"
log_path = os.path.join(log_dir, log_filename)

# 将 stdout 和 stderr 重定向到日志文件
sys.stdout = open(log_path, 'w', encoding='utf-8')
sys.stderr = sys.stdout  # 错误也写入日志

print(f"[{datetime.datetime.now()}] 开始评估任务 user_id={username}, job_id={job_number}")
print(f"使用参数文件: {job_params_file}")


import traceback

try:
    # 执行评估任务
    Evaluate_Task = Task_Evaluator(
        job_params,
        job_params['user_id'],
        job_params['task_id'],
        job_params['job_number']
    )
    Evaluate_Task.get_files() # 从云盘中移动文件到服务器
    print('成功移动用户上传的文件！下面执行评估进程')
    Evaluate_Task.execute_eva() # 执行评估主函数
    print(f"[{datetime.datetime.now()}] 评估完成 ✅")

except Exception as e:
    print(f"[{datetime.datetime.now()}] 评估失败 ❌: {str(e)}")
    print("详细错误信息如下：")
    traceback.print_exc()  # 打印完整 traceback 到日志文件
    sys.exit(1)
finally:
    sys.stdout.flush()
    sys.stdout.close()