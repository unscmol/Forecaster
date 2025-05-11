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
    # 不要给任务加超参数，需要的超参数通过job_params指定就行。
    def process_task1(self): # 直接写后处理逻辑，除了任务关注的东西外，必须要包含并返回 rank_score 变量，用于展示排名。
        # 1. 加载计算好的结果
        data_dir = os.path.join(project_root, 'data')
        test_dic = joblib.load(
            os.path.join(data_dir, 'user_data', str(self.user_id), 'test_job_data', str(self.job_number),
                         'format_test_dic_{}_{}_{}.joblib'.format(self.user_id, self.task_id, self.job_number))
        )
        name_ls = list(test_dic.keys()) # 读入包含每个场的id列表
        '''
        scaler_dic：评估需要用的结果和归一化参数，如果在evaluate_src逻辑中保存了反归一化的超参数，也可以不用再读入scaler_dic
        约定俗成不用反归一化的任务可以直接不管👇不过任务1的评估需要用到每个场站最大值（假设为额定）
        '''
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
        # 2. 遍历每个场站，计算综合精度与排名分
        rank_score = 0 # 建议初始化为0，比没有值好，起码能上榜
        acc_list = []
        for station_id in name_ls:
            scaler = scaler_dic[station_id]  # 加载场站归一化参数
            true, pre = result_dic[station_id]
            scaler_max = scaler.data_max_[0]
            acc = acc_cal(true, pre, scaler_max)
            print('The accuracy of station {} is {}%'.format(station_id, acc))
            acc_list.append(acc)
        rank_score = np.array(acc_list).mean()
        return rank_score

    '''
    别忘了在以下执行方法中添加新任务的映射👇
    '''
    def execute_process(self):
        # 创建任务映射字典, 新建任务需要在字典中关联任务ID和续写的函数
        task_mapping = {
            1: self.process_task1
        }

        task_id = self.task_id

        # 获取对应的方法并执行
        if task_id in task_mapping:
            return task_mapping[task_id]()
        else:
            raise ValueError(f"不支持的任务类型: task_id = {task_id}")