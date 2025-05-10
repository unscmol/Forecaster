# Forecaster

## 目前需要思考的问题与笔记

- [x] 目前新增任务的逻辑是分别在src的相关模块中编写功能代码类的子方法，由统一的功能方法自动调用。
- [x] 完善创建任务的超参数生成格式，提供可选的表单。以字典格式可以方便初始化任务的超参数job_params.json，无需在后端修改。
- [ ] 注册自动创建相关文件夹
- [ ] 测试代码的样本划分也由用户写的话，存在作弊可能性。
  - 通过程序直接规定死测试数据的形状，直接验证。
- [ ] 销毁数据通过定时运行的代码定期检查执行。





## 任务描述

## Taks1：超短期单场功率预测

##### 数据集介绍：

每个场站直接按照时间切片给出训练集和测试集。

##### 你需要上传：

1. 训练好的模型
2. 每个场站模型的类代码，模型类名称必须为：User_Model
3. 每个场站的归一化参数。sklearn库的scaler，用joblib后缀
4. 每个场站的模型实例化超参数。

##### 数据分发：

脚本驱动功能代码自动实现，创建任务后将需要用到的数据储存在用户可访问的文件夹下。





## 各模块详细文字说明

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





## Forecaster系统路径

- config
  - system_config #系统全局配置
  - job_config #作业配置
  - task_config #任务类型配置
- data
  - raw
  - processed
    - archive_data #归档的数据
    - fixed_data #修正后的数据
  - temp
    - cached_data #缓存数据
  - user_data #所有用户长期储存的数据（防止数据量过大也许可以设置定期销毁策略）
- scripts #脚本集
  - user_interaction #用户交互脚本
  - prepare_data #数据准备脚本
  - run_evaluation #运行评估脚本
- src #核心代码
  - data_manager #数据处理与管理
  - model_evaluator #模型设置与评估
  - task_manager #任务管理
  - user_interface #用户交互
  - untils #开发工具箱
- results
  - user_evaluations #用户评估结果
- interactive_space #联网交互文件夹
  - download_data #数据集下载
  - upload_data #用户反馈路径
- misc #杂项



## 跳转说明

<span id="sccllc">上传处理流程：</span>脚本驱动，读取作业号上传的新文件，生成确认提示。



## 草稿

tree /f /a > project_structure.txt
