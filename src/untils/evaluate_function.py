import os
import time
import copy

import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim.lr_scheduler as lr_scheduler
from torch.optim import Adam
from torch.utils.data import TensorDataset, DataLoader, Dataset

import math
import warnings

warnings.filterwarnings("ignore")

def acc_cal(true, pre, cap):
    # 确保输入的形状正确
    if true.shape != pre.shape:
        raise ValueError("The shape of true and pre must be the same.")
    rmse_per_sample = np.sqrt(np.mean((true - pre) ** 2, axis=1)) / cap
    acc = (1 - np.mean(rmse_per_sample)) * 100
    return acc