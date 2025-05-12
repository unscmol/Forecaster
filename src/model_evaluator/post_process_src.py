import os
import sys
import numpy as np
import pandas as pd
import pickle
import shutil
import matplotlib.pyplot as plt
import joblib
import importlib.util

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim.lr_scheduler as lr_scheduler
from torch.optim import Adam
from torch.utils.data import TensorDataset, DataLoader, Dataset

# 计算项目根路径 Forecaster目录下
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# 将自定义模块路径添加到系统路径中
sys.path.append(os.path.join(project_root, 'src', 'untils'))
from evaluate_function import acc_cal

# 启用GPU
GPU_switch = True
device = torch.device("cuda" if (torch.cuda.is_available() and GPU_switch) else "cpu")

class Task_Processor:
    def __init__(self, job_params, user_id, task_id, job_number):
        '''
        :param job_params 任务超参数文件(包含了下列变量)
        :param user_id: 用户名称
        :param task_id: 任务类型
        :param job_number: 作业号，由上层脚本运行次数决定
        '''
        self.user_id = user_id
        self.task_id = task_id
        self.job_number = job_number
        self.para = job_params

    '''Task1评估主函数'''
    def process_task1(self):  # 一定要在最后print(f'RANK_SCORE: {rank_score:.6f}')  # ✅ 必须必须打印，否则不能提取分数！添加这一行用于submit_evaluation提取排名分
        data_dir = os.path.join(project_root, 'data')
        test_dic = joblib.load(
            os.path.join(data_dir, 'user_data', str(self.user_id), 'test_job_data', str(self.job_number),
                         'format_test_dic_{}_{}_{}.joblib'.format(self.user_id, self.task_id, self.job_number))
        )
        name_ls = list(test_dic.keys())
        result_dic, scaler_dic = {}, {}

        for station_id in name_ls:
            result_path = os.path.join(
                data_dir, 'user_data', str(self.user_id), 'test_job_data', str(self.job_number),
                'result_{}_{}_{}_{}.joblib'.format(station_id, self.user_id, self.task_id, self.job_number)
            )
            scaler_path = os.path.join(
                data_dir, 'user_data', str(self.user_id), 'upload_data',
                'scaler_{}_{}_{}_{}.joblib'.format(station_id, self.user_id, self.task_id, self.job_number)
            )
            result_dic[station_id] = joblib.load(result_path)
            scaler_dic[station_id] = joblib.load(scaler_path)

        rank_score = 0
        acc_list = []
        for station_id in name_ls:
            scaler = scaler_dic[station_id]
            true, pre = result_dic[station_id]
            scaler_max = scaler.data_max_[0]
            acc = acc_cal(true, pre, scaler_max)
            print('The accuracy of station {} is {}%'.format(station_id, acc))
            acc_list.append(acc)

        rank_score = np.array(acc_list).mean()
        print(f'RANK_SCORE: {rank_score:.10f}')  # ✅ 必须必须打印，否则不能提取分数！添加这一行用于submit_evaluation提取排名分
        return rank_score

    def execute_process(self):
        task_mapping = {
            1: self.process_task1
        }
        task_id = self.task_id
        if task_id in task_mapping:
            return task_mapping[task_id]()
        else:
            raise ValueError(f"不支持的任务类型: task_id = {task_id}")