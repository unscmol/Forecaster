import os
import sys
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import joblib

#引入自定义函数
sys.path.append(r"C:\Users\ZY\Desktop\Forecaster\src\untils")
from forecaster_fuction import check_missing_values, split_train_test_data_by_time






class Generate_cached_data:
    def __init__(self, total_data_path, user_id, task_id, job_number):
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

    '''Task1数据分发'''
    def gen_task1(self):
        data_dic = joblib.load(self.total_data_path)
        train_data_dic, test_data_dic = split_train_test_data_by_time(data_dic)
        # 临时数据储存
        joblib.dump(train_data_dic, '../interactive_space/download_data/temp_trainset_{}_{}_{}.joblib'.format(self.user_id, self.task_id, self.job_number))
        joblib.dump(train_data_dic, '../data/temp/cached_data/temp_trainset_{}_{}_{}.joblib'.format(self.user_id, self.task_id, self.job_number))
        joblib.dump(test_data_dic, '../data/temp/cached_data/temp_testset_{}_{}_{}.joblib'.format(self.user_id, self.task_id, self.job_number))

    def execute_task(self):
        # 创建任务映射字典
        task_mapping = {
            1: self.gen_task1
        }

        task_id = self.task_id

        # 获取对应的方法并执行
        if task_id in task_mapping:
            return task_mapping[task_id]()
        else:
            raise ValueError(f"不支持的任务类型: task_id = {task_id}")