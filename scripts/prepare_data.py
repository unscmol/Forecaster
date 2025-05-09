import os
import sys
import json
import numpy as np
import pandas as pd
import pickle
import shutil
import matplotlib.pyplot as plt
import joblib

# 引入自定义函数
sys.path.append(r"..\src\untils")
sys.path.append(r"..\src\data_manager")
from forecaster_fuction import check_missing_values, split_train_test_data_by_time
from data_send_src import Generate_cached_data

# 获取传入的参数文件路径
job_params_file = sys.argv[1]  # 获取命令行参数传递的文件路径

# 读取超参数
with open(job_params_file, "r") as f:
    job_params = json.load(f)

'''依据任务读取原始数据，并处理成分发和检验的结果储存'''
# 读取原始数据并生成训练，测试临时文件
Generate_Data = Generate_cached_data(job_params, job_params['total_data_path'], job_params['user_id'], job_params['task_id'], job_params['job_number'])
Generate_Data.execute_task()  # 依据task_id自动选择类方法创建数据文件



