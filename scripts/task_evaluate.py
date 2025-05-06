import os
import sys
import json
import numpy as np
import pandas as pd
import pickle
import shutil
import matplotlib.pyplot as plt
import joblib

#引入自定义函数
sys.path.append(r"..\src\untils")
sys.path.append(r"..\src\model_evaluator")
from forecaster_fuction import check_missing_values, split_train_test_data_by_time
from evaluate_src import Task_Evaluator

# 读取超参数
with open("../config/job_config/job_params.json", "r") as f:
    job_params = json.load(f)

'''依据任务执行评估函数'''
# 读取原始数据并生成训练，测试临时文件
Evaluate_Task = Task_Evaluator(job_params, job_params['user_id'], job_params['task_id'], job_params['job_number'])
Evaluate_Task.execute_eva() # 依据task_id自动选择类方法创建数据文件