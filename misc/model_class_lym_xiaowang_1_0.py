import os
import sys
import json
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import joblib

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim.lr_scheduler as lr_scheduler
from torch.optim import Adam
from torch.utils.data import TensorDataset, DataLoader, Dataset


import warnings

warnings.filterwarnings("ignore")

class GRU_Encoder(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super(GRU_Encoder, self).__init__()
        self.hidden_dim = hidden_dim
        self.gru = nn.GRU(input_dim, hidden_dim, batch_first=True)
        self.fc_out = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        out, hn = self.gru(x)
        pre_power = self.fc_out(hn)
        return pre_power.permute(1, 0, 2)