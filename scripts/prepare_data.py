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

# 引入自定义函数
sys.path.append(r"..\src\untils")
sys.path.append(r"..\src\data_manager")
from forecaster_fuction import check_missing_values, split_train_test_data_by_time
from data_send_src import Generate_cached_data

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

log_filename = f"prepare_data_{username}_jobid{job_number}.log"
log_path = os.path.join(log_dir, log_filename)

# 重定向 stdout 和 stderr 到日志文件
sys.stdout = open(log_path, 'w', encoding='utf-8')
sys.stderr = sys.stdout

print(f"[{datetime.datetime.now()}] 开始准备数据 user_id={username}, job_id={job_number}")
print(f"使用参数文件: {job_params_file}")

import traceback

try:
    # 执行数据准备任务
    Generate_Data = Generate_cached_data(
        job_params,
        job_params['total_data_path'],
        job_params['user_id'],
        job_params['task_id'],
        job_params['job_number']
    )
    Generate_Data.execute_task()
    print(f"[{datetime.datetime.now()}] 数据准备完成 ✅")

except Exception as e:
    print(f"[{datetime.datetime.now()}] 数据准备失败 ❌: {str(e)}")
    print("详细错误信息如下：")
    traceback.print_exc()

finally:
    sys.stdout.flush()
    sys.stdout.close()