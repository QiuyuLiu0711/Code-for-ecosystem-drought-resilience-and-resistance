import pandas as pd
import os

# 设置输入文件夹路径
input_directory = ' '

# 获取所有 .txt 文件的列表
txt_files = [f for f in os.listdir(input_directory) if f.endswith('.txt')]

# 手动输入需要计算的变量
statistical_variables = ['resilience', 'resistance','Z_PDSI']

# 手动输入需要计算的年份范围
start_year = 2015
end_year = 2100

# 生成年份列表
selected_years = list(range(start_year, end_year + 1))

# 初始化一个空的 DataFrame 用于存储所有数据
all_data = pd.DataFrame()

# 循环读取每个 .txt 文件
for txt_file in txt_files:
    # 构建文件路径
    file_path = os.path.join(input_directory, txt_file)

    # 读取 .txt 文件，假设使用制表符分隔
    data = pd.read_csv(file_path, sep='\t')

    # 筛选出特定年份的数据
    filtered_data = data[data['Year'].isin(selected_years)]

    # 将所有需要计算的指标数据保留到 filtered_data
    filtered_data = filtered_data[['Year', 'Plot_ID', 'Lat', 'Type'] + statistical_variables]

    # 合并到总的数据框
    all_data = pd.concat([all_data, filtered_data], ignore_index=True)

# 计算各个 Plot_ID 在特定年份的均值
plot_id_means_specific_years = all_data.groupby('Plot_ID')[statistical_variables].mean().reset_index()

# 计算各个年份所有 Plot_ID 的均值和标准差
year_stats_specific_years = all_data.groupby('Year')[statistical_variables].agg(['mean', 'std']).reset_index()

# 计算不确定性的上下限
for variable in statistical_variables:
    year_stats_specific_years[(variable, 'lower')] = year_stats_specific_years[(variable, 'mean')] - year_stats_specific_years[(variable, 'std')]
    year_stats_specific_years[(variable, 'upper')] = year_stats_specific_years[(variable, 'mean')] + year_stats_specific_years[(variable, 'std')]

# 将多层索引列展平，转换为单层索引
year_stats_specific_years.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in year_stats_specific_years.columns]

# **基于纬度 Lat 计算平均值，并将其按 0.5 度分箱**
all_data['Lat_bin'] = pd.cut(all_data['Lat'], bins=[x * 0.5 for x in range(int(all_data['Lat'].min() * 2), int(all_data['Lat'].max() * 2) + 2)])

# 提取每个分箱的中间值
lat_bin_mid = all_data['Lat_bin'].apply(lambda x: (x.left + x.right) / 2)

# 将中间值添加到数据框中
all_data['Lat_bin_mid'] = lat_bin_mid

# 按 Lat_bin 计算各个统计变量的平均值，并包括 Lat_bin_mid
lat_bin_means = all_data.groupby('Lat_bin')[statistical_variables].mean().reset_index()

# 计算并添加中间值列
lat_bin_means['Lat_bin_mid'] = lat_bin_means['Lat_bin'].apply(lambda x: (x.left + x.right) / 2)

# **按 0.5 度间隔分箱后的纬度计算各年份的平均值**
lat_bin_year_means = all_data.groupby(['Year', 'Lat_bin'])[statistical_variables].mean().reset_index()

# 计算并添加中间值列
lat_bin_year_means['Lat_bin_mid'] = lat_bin_year_means['Lat_bin'].apply(lambda x: (x.left + x.right) / 2)

# **基于植被类型 Type 计算 'resilience' 和 'resistance' 的平均值**
type_means = all_data.groupby('Type')[statistical_variables].mean().reset_index()

# **基于森林类型 Type 计算各个类型在各年份的平均值**
type_year_means = all_data.groupby(['Year', 'Type'])[statistical_variables].mean().reset_index()

# **基于纬度 Lat 计算各个纬度在各年份的平均值**
lat_year_means = all_data.groupby(['Year', 'Lat'])[statistical_variables].mean().reset_index()

# 确保输出目录存在
output_directory = ' '
os.makedirs(output_directory, exist_ok=True)

# 保存各个 Plot_ID 在所有年份各个变量的平均值到 Excel 文件
plot_id_output_path = os.path.join(output_directory, 'plot_id_means_specific_years_SSP3.xlsx')
plot_id_means_specific_years.to_excel(plot_id_output_path, index=False, sheet_name='Plot_ID_Means')

# 保存各个年份所有 Plot_ID 的平均值和不确定性到 Excel 文件
year_stats_output_path = os.path.join(output_directory, 'year_stats_specific_years_SSP3.xlsx')
year_stats_specific_years.to_excel(year_stats_output_path, index=False, sheet_name='Year_Stats')

# **保存基于分箱后的纬度 Lat_bin 的平均值到 Excel 文件**
lat_bin_means_output_path = os.path.join(output_directory, 'lat_bin_means_SSP3.xlsx')
lat_bin_means.to_excel(lat_bin_means_output_path, index=False, sheet_name='Lat_Bin_Means')

# **保存基于植被类型 Type 的平均值到 Excel 文件**
type_means_output_path = os.path.join(output_directory, 'type_means_SSP3.xlsx')
type_means.to_excel(type_means_output_path, index=False, sheet_name='Type_Means')

# **保存基于森林类型 Type 在各年份的平均值**
# 对于 type_year_means_SSP1.xlsx 中的不同 Type 分别保存成不同的 Excel 文件
for type_value in type_year_means['Type'].unique():
    type_specific_data = type_year_means[type_year_means['Type'] == type_value]
    type_output_path = os.path.join(output_directory, f'type_year_means_{type_value}_SSP3.xlsx')
    type_specific_data.to_excel(type_output_path, index=False, sheet_name=f'{type_value}_Year_Means')

# **保存按 0.5 度间隔分箱后的纬度在各年份的平均值到 Excel 文件**
lat_bin_year_means_output_path = os.path.join(output_directory, 'lat_bin_year_means_SSP3.xlsx')
lat_bin_year_means.to_excel(lat_bin_year_means_output_path, index=False, sheet_name='Lat_Bin_Year_Means')

# **将 'Lat_bin_mid' 列转换为 float 类型，修复类型错误**
lat_bin_means['Lat_bin_mid'] = lat_bin_means['Lat_bin_mid'].astype(float)

# **根据 Lat_bin_mid 分割 lat_bin_means_SSP1.xlsx**
# 保存 Lat_bin_mid 大于 0 的数据
lat_bin_means_positive = lat_bin_means[lat_bin_means['Lat_bin_mid'] > 0]
lat_bin_means_positive_output_path = os.path.join(output_directory, 'lat_bin_means_positive_SSP3.xlsx')
lat_bin_means_positive.to_excel(lat_bin_means_positive_output_path, index=False, sheet_name='Lat_Bin_Means_Positive')

# 保存 Lat_bin_mid 小于 0 的数据
lat_bin_means_negative = lat_bin_means[lat_bin_means['Lat_bin_mid'] < 0]
lat_bin_means_negative_output_path = os.path.join(output_directory, 'lat_bin_means_negative_SSP3.xlsx')
lat_bin_means_negative.to_excel(lat_bin_means_negative_output_path, index=False, sheet_name='Lat_Bin_Means_Negative')

# 打印确认信息
print("所有数据已保存为 Excel 文件。")
