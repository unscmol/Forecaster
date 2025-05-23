import os
import sys
import numpy as np
import pandas as pd
import pickle
import shutil
import matplotlib.pyplot as plt
import joblib

#引入自定义函数
sys.path.append(r"C:\Users\ZY\Desktop\Forecaster\src\untils")
from forecaster_fuction import check_missing_values, split_train_test_data_by_time






class Generate_cached_data:
    def __init__(self, job_params, total_data_path, user_id, task_id, job_number):
        '''

        :param total_data_path: 原始数据字典路径
        :param user_id: 用户名称
        :param task_id: 任务类型
        :param job_number: 作业号，由上层脚本运行次数决定
        '''
        self.total_data_path = total_data_path
        self.user_id = user_id
        self.task_id = task_id
        self.job_number = job_number

        self.para = job_params

    '''Task1数据分发'''
    def gen_task1(self): # 注意任务数据准备函数的相对路径是以脚本prepare_data.cmd为准的；不要在任务流函数中添加参数!可以在job_params添加需要的额外参数；

        # 1. 从数据库中获取数据并处理为临时的训练集和测试集保存在临时路径下
        data_dic = joblib.load(self.total_data_path)
        train_data_dic, test_data_dic = split_train_test_data_by_time(data_dic=data_dic, train_ratio=0.8)
        # 储存任务所需数据
        joblib.dump(train_data_dic, '../data/user_data/{}/download_data/temp_trainset_{}_{}_{}.joblib'.format(self.user_id, self.user_id, self.task_id, self.job_number))
        joblib.dump(train_data_dic,
                    '../interactive_space/{}/download_data/temp_trainset_{}_{}_{}.joblib'.format(self.user_id,
                                                                                              self.user_id,
                                                                                              self.task_id,
                                                                                              self.job_number))
        joblib.dump(test_data_dic, '../data/user_data/{}/download_data/temp_testset_{}_{}_{}.joblib'.format(self.user_id, self.user_id, self.task_id, self.job_number))


        # 2. 数测试数据的处理（如果是要统一测试集形状格式的可以添加代码）
        '''目前temp_testset_{}_{}_{}.joblib只是做个备份，需要自定义评估代码的用户才需要调用到这个文件，不然都是在下面写好固定测试集的形状，统一测试的'''
        def create_data(data_n, inp_len, out_len, step_len): # 可以嵌套函数，方便内部调用
            inp_data, dec_inp, out_data = [], [], []
            for i in range(0, data_n.shape[0] - inp_len - out_len, step_len):  # 没有缺失值
                if not np.isnan(data_n[i:i + inp_len]).any() and not np.isnan(
                        data_n[i + inp_len:i + inp_len + out_len]).any():
                    inp_data.append(data_n[i:i + inp_len, 0])
                    # dec_inp.append(data_n[i:i + inp_len, 1])
                    out_data.append(data_n[i + inp_len:i + inp_len + out_len, 0])
            inp_data, out_data = np.stack(inp_data), np.stack(out_data)
            return inp_data.reshape(-1, out_len, 1), out_data.reshape(-1, out_len, 1)

        name_list = list(test_data_dic.keys())
        test_dic = {}
        for name in name_list:
            origin_data = test_data_dic[name]
            data_test = np.array(origin_data.iloc[:, 1]).reshape(-1,1) # 取出power列
            inp_data, out_data = create_data(data_test, self.para['inp_len'], self.para['out_len'], self.para['step_len'])
            test_dic[name] = [inp_data, out_data]
        # 目标路径
        path = f'../data/user_data/{self.user_id}/test_job_data/{self.job_number}'
        # 如果路径不存在，创建路径
        os.makedirs(path, exist_ok=True)
        # 保存文件
        file_path = os.path.join(path, f'format_test_dic_{self.user_id}_{self.task_id}_{self.job_number}.joblib')
        joblib.dump(test_dic, file_path)
        print('Success saving test data in user_data folder!')

    def execute_task(self):
        # 创建任务映射字典, 新建任务需要在字典中关联任务ID和续写的函数
        task_mapping = {
            1: self.gen_task1
        }

        task_id = self.task_id

        # 获取对应的方法并执行
        if task_id in task_mapping:
            return task_mapping[task_id]()
        else:
            raise ValueError(f"不支持的任务类型: task_id = {task_id}")