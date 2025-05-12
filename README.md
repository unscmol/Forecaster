# Forecaster👉一个功率预测科研管理平台

## 目前需要思考的问题与笔记

- [x] 目前新增任务的逻辑是分别在src的相关模块中编写功能代码类的子方法，由统一的功能方法自动调用。
- [x] 完善创建任务的超参数生成格式，提供可选的表单。以字典格式可以方便初始化任务的超参数job_params.json，无需在后端修改。
- [x] 注册自动创建相关文件夹
- [ ] 测试代码的样本划分也由用户写的话，存在作弊可能性。
  - 通过程序直接规定死测试数据的形状，直接验证。
- [x] web端需要添加新建文件夹功能
- [x] 结束作业逻辑需要完善，本质上是数据库中作业状态变量的修改与调用系统的完善。
- [ ] 冗余数据检索删除功能应该是定时执行的，通过作业号和文件后缀检索相关目录下对应文件。暂定是user_data下标记为Finishing的任务数据
- [ ] 若用户上传的模型类比较复杂，在一个py文件中定义了很多类，主类命名为User_Model，还能实现服务器的实例化吗？
- [x] 请用户主动把废弃的作业结束，以便清空服务器空间。若是比较重要想保留所有备份记录的作业，设计收藏作业的功能，把作业状态设置为“Favored”。设计整理任务列表功能，用户可以在主页一键删除状态为Finishing的作业条目，并按作业号顺序置顶状态为“Favored”的作业。
- [ ] 添加能够批量上传多个文件的功能
- [ ] 添加删除选中作业的功能，主页





## 任务描述

## Taks1：超短期单场功率预测

##### 数据集介绍：

每个场站直接按照时间切片给出训练集和测试集。

##### 你需要上传：

1. 训练好的模型

2. 每个场站模型的类代码，模型类名称必须为：User_Model

   命名格式为"model_class_cl_xiaowang_1_14.py"，文件内import必要的库后直接定义你的模型class即可，主模型类名设置为User_Model

3. 每个场站的归一化参数。sklearn库的scaler，用joblib后缀

4. 每个场站的模型实例化超参数

   字典格式储存为"model_class_hyperparams_用户名\_任务类型\_作业号.joblib“，其中每个键名为场站名称，值为实例化模型的参数字典变量，示例如下：

   ```python
   {'cl': {'input_dim': 1, 'hidden_dim': 128},
    'js': {'input_dim': 1, 'hidden_dim': 128},
    'jz': {'input_dim': 1, 'hidden_dim': 128},
    'lym': {'input_dim': 1, 'hidden_dim': 128},
    'qss': {'input_dim': 1, 'hidden_dim': 128},
    'wtl': {'input_dim': 1, 'hidden_dim': 128},
    'zh': {'input_dim': 1, 'hidden_dim': 128}}
   ```

   

##### 数据分发：

脚本驱动功能代码自动实现，创建任务后将需要用到的数据储存在用户可访问的文件夹下。

##### 排名分计算方法：

计算每个场站的[标准准确率](#acc_cal)，并场级平均。



## 项目各模块说明

**关于interactive_space**

其中的文件可供所有用户ssh访问自己的文件夹，每个用户注册后会自动生成“用户名”的文件夹。

download_data中用job_id定位的文件，在job完成指令下达后自动删除。

upload_data中的用job_id定位的文件，用户确认上传后服务器启动[上传处理流程](#sccllc)，作业完成后自动删除。

**关于src**

主要代码全部在此文件夹下，对应模块的功能写成类的形式，添加功能需要在类中添加方法函数，execute_函数中通过任务类型自动调用对应的新方法。

**关于src-data_manager**

每个任务的固定测试集比例在此调整。



**web_interface**

注意：迁移项目时修改Forecaster\web_interface\mainapp\views.py中的main_path



## 使用说明

### 如何创建任务？

#### 第一步：增添逻辑代码

#### 第二步：定义任务默认的超参数

需要在“Forecaster\config\system_config\task_default_config”下保存默认任务参数，
示例如下：

```python
job_params = {
            "total_data_path": "../data/processed/archive_data/dataset_1/total_data_dic.joblib",
            "user_id": "xiaowang",
            "task_id": 1,  # 任务类型1
            "job_number": 0,  # 使用数据库自动生成的 job_id
            "inp_len": 16,
            "out_len": 16,
            "step_len": 1,
            "Custom_evaluation": 0
        }
```

**其中必须包含：**
total_data_path：原始数据库对应的数据路径，方便前面写的逻辑代码调用
user_id：任务发布者在服务器测试任务时默认用xiaowang登入，无需修改
task_id：依据新建任务的代码填写，写错问题也不大，网页端会根据所选内容覆盖实际参数值
job_number：所有新建任务测试代码的任务号都用0，避免意想不到的bug。

**其他超参数：**
剩下的超参数依据具体任务需求由设计任务逻辑代码的人规定。作用就是你的任务逻辑代码中需要调用到的都可以写进去。因为只是默认值，并且web端用户可以自己编写超参数进行合并，因此些什么完全取决于实际情况，不写的话就在描述任务细节部分说清楚用户自己需要写的超参数。

#### 第三步：web描述任务细节



### 关于提交评估

目前你可以在作业细节界面随时提交任何一个作业的评估，不论作业状态是什么。启动评估后，后台会从云盘中把作业ID相关的文件全部转移到服务器内部，如果你没上传文件，系统会从后台用户备份文件中使用以前该作业的文件。如果你上传了新的文件，那么会直接覆盖掉系统数据库中相同作业号的相关文件，所以请谨慎操作。

若评估过程出现bug，作业状态会保持为Pending，你可以在云盘中的download_data文件夹下找到反馈的相关日志以便debug；若评估成功，作业状态会变为Finishing



### 用户注册

直接在web端操作即可。系统会在Forecaster\data\user_data和Forecaster\interactive_space生成用户文件夹。

### 用户注销

首先在web管理员界面删除用户帐号，然后需要在Forecaster\data\user_data和Forecaster\interactive_space中直接用cmd删除用户的文件夹。





## 跳转说明

<span id="sccllc">上传处理流程：</span>脚本驱动，读取作业号上传的新文件，生成确认提示。

<span id="acc_cal">标准准确率：</span>计算代码如下：

```python
def acc_cal(true, pre, cap): # true和pre分别是2维numpy数组，维度分别是(样本，预测步长)；cap是额定
    # 确保输入的形状正确
    if true.shape != pre.shape:
        raise ValueError("The shape of true and pre must be the same.")
    rmse_per_sample = np.sqrt(np.mean((true - pre) ** 2, axis=1)) / cap
    acc = (1 - np.mean(rmse_per_sample)) * 100
    return acc
```




## 草稿

tree /f /a > project_structure.txt

rd/s/q F:\AdobePhotoshop\Adobe Photoshop CS6 # 删除文件夹cmd

