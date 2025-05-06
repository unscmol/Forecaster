import shutil
import os
import sys
import json
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import joblib

def copy_model_class(source_filename, target_filename):
    # 检查源文件是否存在
    if os.path.exists(source_filename):
        # 使用 shutil 复制文件
        shutil.copy(source_filename, target_filename)
        print(f"文件已成功复制到: {target_filename}")
    else:
        print(f"源文件 {source_filename} 不存在！")


if __name__ == "__main__":
    with open("../config/job_config/job_params.json", "r") as f:
        job_params = json.load(f)
    test_dic = joblib.load('../data/user_data/{}/test_job_data/format_test_dic_{}_{}_{}.joblib'.format(job_params['user_id'], job_params['user_id'], job_params['task_id'], job_params['job_number']))
    name_ls = list(test_dic.keys())
    # 设置源文件名和目标文件名
    for name in name_ls:
        source_file = "model_class.py"
        target_file = "model_class_{}_{}_{}_{}.py".format(name, job_params['user_id'], job_params['task_id'], job_params['job_number'])  # 你可以更改这个文件名为你需要的文件名

        copy_model_class(source_file, target_file)