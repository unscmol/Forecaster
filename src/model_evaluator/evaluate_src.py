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
sys.path.append(os.path.join(project_root, 'data', 'untils'))
from evaluate_function import acc_cal
# 启用GPU
GPU_switch = True
device = torch.device("cuda" if (torch.cuda.is_available() and GPU_switch) else "cpu")

class Task_Evaluator:
    def __init__(self, job_params, user_id, task_id, job_number):
        '''
        :param user_id: 用户名称
        :param task_id: 任务类型
        :param job_number: 作业号，由上层脚本运行次数决定
        '''
        self.user_id = user_id
        self.task_id = task_id
        self.job_number = job_number
        self.para = job_params
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

    '''Task1评估主函数'''
    def eva_task1(self): # 注意任务数据准备函数的相对路径是以脚本.cmd为准的；不要在任务流函数中添加参数!可以在job_params添加需要的额外参数；
        # 1. 加载固定的测试数据并处理
        # 读入测试数据
        # 构建基础路径
        data_dir = os.path.join(self.project_root, 'data')
        test_dic = joblib.load(
            os.path.join(data_dir, 'user_data', str(self.user_id), 'test_job_data', str(self.job_number),
                         'format_test_dic_{}_{}_{}.joblib'.format(self.user_id, self.task_id, self.job_number))
        )
        # 读入模型超参数字典
        model_class_hyperparams = joblib.load(
            os.path.join(data_dir, 'user_data', str(self.user_id), 'upload_data',
                         'model_class_hyperparams_{}_{}_{}.joblib'.format(self.user_id, self.task_id, self.job_number))
        )
        name_ls = list(test_dic.keys())
        pth_dic, scaler_dic, model_dic = {}, {}, {}
        for station_id in name_ls:
            # 读入对应场站模型参数
            pth_path = os.path.join(
                data_dir, 'user_data', str(self.user_id), 'upload_data',
                'model_para_{}_{}_{}_{}.pth'.format(station_id, self.user_id, self.task_id, self.job_number)
            )
            pth_dic[station_id] = torch.load(pth_path)
            # 读入对应场站归一化参数
            scaler_path = os.path.join(
                data_dir, 'user_data', str(self.user_id), 'upload_data',
                'scaler_{}_{}_{}_{}.joblib'.format(station_id, self.user_id, self.task_id, self.job_number)
            )
            scaler_dic[station_id] = joblib.load(scaler_path)

            # 构造模型文件的绝对路径
            model_file_path = os.path.join(self.project_root, 'data', 'user_data', self.user_id, 'upload_data',
                                           f'model_class_{station_id}_{self.user_id}_{self.task_id}_{self.job_number}.py')

            model_hyperpara = model_class_hyperparams[station_id] # 读入实例化的超参数
            # 获取模型文件路径
            spec = importlib.util.spec_from_file_location("User_Model_{}".format(station_id), model_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 获取模型类 User_Model 并实例化
            model_class = getattr(module, "User_Model")
            model_dic[station_id] = model_class(**model_hyperpara)  # 实例化模型

            # 加载模型参数
            model_dic[station_id].load_state_dict(pth_dic[station_id])

        # 3. 测试主流程
        # 3.1 读入数据并处理成batchsize为1
        for station_id in name_ls:
            model = model_dic[station_id] # 加载场站模型
            scaler = scaler_dic[station_id] # 加载场站归一化参数
            inp_data_v, out_data_v = test_dic[station_id]  # 加载场站测试集[sample, 16, 1]
            inp_v, out_v = torch.tensor(inp_data_v, dtype=torch.float32), torch.tensor(out_data_v, dtype=torch.float32)
            test_loader = DataLoader(TensorDataset(inp_v, out_v), shuffle=False, batch_size=1)
            # 3.2 开始测试
            true_data, pre_data = [], []
            model.eval()
            model.to(device)
            with torch.no_grad():
                for batch_idx, (inp_x, yy) in enumerate(test_loader):
                    inp_x, yy = inp_x.to(device), yy.to(device)
                    # 归一化输入
                    scaler_max, scaler_min = scaler.data_max_[0], scaler.data_min_[0]
                    inp_x_normalized = (inp_x - scaler_min) / (scaler_max - scaler_min)
                    pred = model(inp_x_normalized)

                    pred_denormalized = pred * (scaler_max - scaler_min) + scaler_min

                    if yy.shape[0] != 1:
                        true_data.append(yy.cpu().numpy().squeeze())
                        pre_data.append(pred_denormalized.cpu().numpy().squeeze())
                    else:
                        true_data.append(yy.cpu().numpy().reshape(1, -1))
                        pre_data.append(pred_denormalized.cpu().numpy().reshape(1, -1))

            true = np.concatenate(true_data, axis=0)
            pre = np.concatenate(pre_data, axis=0)

            result_path = os.path.join(
                data_dir, 'user_data', str(self.user_id), 'test_job_data', str(self.job_number),
                'result_{}_{}_{}_{}.joblib'.format(station_id, self.user_id, self.task_id, self.job_number)
            )
            joblib.dump([true, pre], result_path)

            acc = acc_cal(true, pre, scaler_max)
            print('The accuracy of station {} is {}%'.format(station_id, acc))

    def execute_eva(self):
        # 创建任务映射字典, 新建任务需要在字典中关联任务ID和续写的函数
        task_mapping = {
            1: self.eva_task1
        }

        task_id = self.task_id

        # 获取对应的方法并执行
        if task_id in task_mapping:
            return task_mapping[task_id]()
        else:
            raise ValueError(f"不支持的任务类型: task_id = {task_id}")

    def get_files(self):
        upload_dir = os.path.join(self.project_root, 'interactive_space', str(self.user_id), 'upload_data')
        userdata_dir = os.path.join(self.project_root, 'data', 'user_data', str(self.user_id), 'upload_data')

        for filename in os.listdir(upload_dir):
            # 仅复制以 _{job_number} 结尾的文件（不含扩展名部分）
            if filename.rstrip().rsplit('.', 1)[0].endswith(f"_{self.job_number}"):
                src_path = os.path.join(upload_dir, filename)
                dst_path = os.path.join(userdata_dir, filename)
                if os.path.isfile(src_path):
                    shutil.move(src_path, dst_path)
                    print(f"文件已移动: {src_path} -> {dst_path}")