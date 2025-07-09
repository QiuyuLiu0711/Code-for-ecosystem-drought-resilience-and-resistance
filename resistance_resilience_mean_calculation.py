import pandas as pd
import os

# 读取数据
input_path = ' t'
data = pd.read_csv(input_path, sep='\t')

# 手动输入需要计算的年份范围
start_year = 2015
end_year = 2100

# 生成年份列表
selected_years = list(range(start_year, end_year + 1))

# 筛选出特定年份的数据
filtered_data = data[data['year'].isin(selected_years)]

# 计算各个 Plot_ID 在特定年份的 resistance、resilience、Ye、Ypre、Ypost 平均值
plot_id_means_specific_years = filtered_data.groupby('Plot_ID').agg({
    'resistance': 'mean',
    'resilience': 'mean',
    'Ye': 'mean',
    'Ypre': 'mean',
    'Ypost': 'mean'
}).reset_index()

# 计算各个年份所有 Plot_ID 的 resistance、resilience、Ye、Ypre、Ypost 平均值和标准差
year_stats_specific_years = filtered_data.groupby('year').agg({
    'resistance': ['mean', 'std'],
    'resilience': ['mean', 'std'],
    'Ye': ['mean', 'std'],
    'Ypre': ['mean', 'std'],
    'Ypost': ['mean', 'std']
}).reset_index()

# 计算不确定性的上下限
for variable in ['resistance', 'resilience', 'Ye', 'Ypre', 'Ypost']:
    year_stats_specific_years[(variable, 'lower')] = year_stats_specific_years[(variable, 'mean')] - year_stats_specific_years[(variable, 'std')]
    year_stats_specific_years[(variable, 'upper')] = year_stats_specific_years[(variable, 'mean')] + year_stats_specific_years[(variable, 'std')]

# 打印结果
print("各个 Plot_ID 在特定年份的平均值：")
print(plot_id_means_specific_years)

print("\n各个年份所有 Plot_ID 的平均值和不确定性：")
print(year_stats_specific_years)

# 确保输出目录存在
output_directory = ' '
os.makedirs(output_directory, exist_ok=True)

# 保存各个 Plot_ID 在所有年份各个变量的平均值到文件
plot_id_output_path = os.path.join(output_directory, 'plot_id_means_specific_years.txt')
with open(plot_id_output_path, 'w') as f:
    f.write("各个 Plot_ID 在特定年份的平均值：\n")
    plot_id_means_specific_years.to_csv(f, sep='\t', index=False)

# 保存各个年份所有 Plot_ID 的平均值和不确定性到文件
year_stats_output_path = os.path.join(output_directory, 'year_stats_specific_years.txt')
with open(year_stats_output_path, 'w') as f:
    f.write("各个年份所有 Plot_ID 的平均值和不确定性：\n")
    year_stats_specific_years.to_csv(f, sep='\t', index=False)
