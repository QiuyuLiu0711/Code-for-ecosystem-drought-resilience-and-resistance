import os
import pandas as pd
import numpy as np
from scipy.stats import linregress

# 输入和输出文件夹路径
input_folder = r""
output_file = r" "

# 用户需要手动输入需要拟合的变量名称
variables_to_fit = ["resistance", "resilience", "Z_PDSI"]

# 用户需要手动输入拟合的年份范围
start_year = 2000
end_year = 2100

# 初始化一个空的 DataFrame，用于保存拟合结果
results = []

# 遍历输入文件夹中的所有 .txt 文件
for file_name in os.listdir(input_folder):
    if file_name.endswith(".txt"):
        # 构建文件路径
        file_path = os.path.join(input_folder, file_name)

        # 读取数据
        data = pd.read_csv(file_path, sep="\t")  # 假设是以制表符分隔的文件

        # 确保数据包含必须的列
        required_columns = {"Plot_ID", "Year", "Lat", "Lon"}.union(variables_to_fit)
        if not required_columns.issubset(data.columns):
            print(f"文件 {file_name} 缺少必要的列，已跳过。")
            continue

        # 按 Plot_ID 分组
        for plot_id, group in data.groupby("Plot_ID"):
            # 获取该 Plot_ID 的纬度和经度
            lat = group["Lat"].iloc[0]
            lon = group["Lon"].iloc[0]

            # 过滤年份范围
            group = group[(group["Year"] >= start_year) & (group["Year"] <= end_year)]

            # 如果筛选后没有足够的数据，跳过
            if group.empty:
                print(f"Plot_ID {plot_id} 在年份范围 {start_year}-{end_year} 中无数据，已跳过。")
                continue

            # 初始化结果字典
            result_row = {
                "Plot_ID": plot_id,
                "Lat": lat,
                "Lon": lon
            }

            # 对每个指定的变量进行线性拟合
            for variable in variables_to_fit:
                if variable in group.columns:
                    # 去除 NaN 值
                    valid_data = group.dropna(subset=["Year", variable])

                    # 统计有效数据点的数量
                    count = len(valid_data)

                    # 如果有效数据点不足以进行拟合，则记录空值
                    if count < 2:
                        print(f"Plot_ID {plot_id} 的变量 {variable} 有效数据不足，已跳过。")
                        continue

                    # 线性拟合
                    x = valid_data["Year"]
                    y = valid_data[variable]
                    slope, intercept, r_value, p_value, std_err = linregress(x, y)

                    # 只保存 P < 0.05 的结果
                    if p_value < 0.05:
                        result_row[f"{variable}_R_squared"] = r_value**2
                        result_row[f"{variable}_P_value"] = p_value
                        result_row[f"{variable}_Slope"] = slope
                        result_row[f"{variable}_Count"] = count

            # 如果当前 Plot_ID 有任何显著结果，则保存
            if any(key.startswith(variable) for variable in variables_to_fit for key in result_row.keys()):
                results.append(result_row)

# 将结果保存到 CSV 文件
results_df = pd.DataFrame(results)
results_df.to_csv(output_file, index=False)

print(f"线性拟合结果已保存到 {output_file}")
