
# 缺失值检查函数
def check_missing_values(data_dictionary, columns_to_check=None, key_name_column='key_name', verbose=True):
    """
    检查字典中多个DataFrame的缺失值情况

    参数:
    data_dictionary (dict): 字典，其中键是标识符，值是DataFrame
    columns_to_check (list, optional): 要检查缺失值的列名列表。默认为None，表示检查所有列
    key_name_column (str, optional): 添加到缺失值DataFrame中的列名，用于标识数据来源。默认为'key_name'
    verbose (bool, optional): 是否打印详细统计信息。默认为True

    返回:
    tuple: (missing_values_info, all_missing_dfs)
        - missing_values_info: 包含每个键的缺失值统计信息的字典
        - all_missing_dfs: 包含所有含缺失值的DataFrame的列表
    """
    # 创建一个字典来存储每个键的缺失值信息
    missing_values_info = {}

    # 创建一个列表来存储所有含缺失值的DataFrame
    all_missing_dfs = []

    # 遍历字典中的每个键值对
    for key, df in data_dictionary.items():
        # 确定要检查的列
        if columns_to_check is None:
            cols_to_check = df.columns
        else:
            # 确保指定的列存在于DataFrame中
            cols_to_check = [col for col in columns_to_check if col in df.columns]
            if not cols_to_check:
                if verbose:
                    print(f"警告: {key} 中没有找到任何指定的列，将检查所有列")
                cols_to_check = df.columns

        # 检查指定列的缺失值
        missing_mask = df[cols_to_check].isna().any(axis=1)

        # 如果有缺失值
        if missing_mask.any():
            # 提取含有缺失值的行，保留原始index和列名
            missing_df = df.loc[missing_mask].copy()

            # 添加一列表示数据来源，便于在合并后识别
            missing_df[key_name_column] = key

            # 添加到汇总列表中
            all_missing_dfs.append(missing_df)

            # 创建变量缺失值统计
            variable_breakdown = {}
            for col in cols_to_check:
                variable_breakdown[col] = df[col].isna().sum()

            # 创建一个缺失值统计信息字典
            missing_details = {
                'total_missing_rows': len(missing_df),
                'missing_percentage': (len(missing_df) / len(df)) * 100,
                'variable_breakdown': variable_breakdown
            }

            # 存储到总信息字典中
            missing_values_info[key] = missing_details
        else:
            # 如果没有缺失值，记录为完整数据
            missing_values_info[key] = "No missing values"

    # 如果需要打印详细统计信息
    if verbose:
        # 输出缺失值统计信息
        print("缺失值统计信息:")
        for key, info in missing_values_info.items():
            if info == "No missing values":
                print(f"{key}: 数据完整，没有缺失值")
            else:
                print(
                    f"{key}: 共有 {info['total_missing_rows']} 行缺失值 (占总行数的 {info['missing_percentage']:.2f}%)")
                for var, count in info['variable_breakdown'].items():
                    if count > 0:
                        print(f"  - {var}: {count} 个缺失值")

        # 输出含缺失值的DataFrame列表信息
        print(f"\n共有 {len(all_missing_dfs)} 个键存在缺失值")
        for i, missing_df in enumerate(all_missing_dfs):
            key = missing_df[key_name_column].iloc[0]
            print(f"{i + 1}. {key}: {len(missing_df)} 行缺失值")

        # 如果有缺失值DataFrame，显示第一个的示例
        if all_missing_dfs:
            print("\n第一个含缺失值数据集的部分数据示例:")
            print(all_missing_dfs[0].head())

    return missing_values_info, all_missing_dfs



def split_train_test_data_by_time(data_dic, train_ratio=0.8):
    """
    将data_dic中的每个数据框按照时间顺序划分为训练集和测试集。

    参数:
    -----------
    data_dic : dict
        包含各风电场数据框的字典。
    train_ratio : float, 默认=0.8
        用于训练的数据比例（取值0到1之间）。

    返回:
    --------
    train_data_dic : dict
        包含各风电场训练数据框的字典。
    test_data_dic : dict
        包含各风电场测试数据框的字典。
    """
    train_data_dic = {}
    test_data_dic = {}

    for station_id, df in data_dic.items():
        # 确保数据已按时间排序（如果没有，请取消下面的注释）
        # df = df.sort_index()  # 如果索引是时间戳
        # 或者，如果有时间列
        # df = df.sort_values('时间列名')

        # 计算训练集的边界索引
        train_size = int(len(df) * train_ratio)

        # 按照时间顺序划分数据集
        train_df = df.iloc[:train_size].copy()
        test_df = df.iloc[train_size:].copy()


        # 存储划分结果
        train_data_dic[station_id] = train_df
        test_data_dic[station_id] = test_df

        print(f"场站 {station_id}: 训练集大小 = {len(train_df)}, 测试集大小 = {len(test_df)}")

    return train_data_dic, test_data_dic



