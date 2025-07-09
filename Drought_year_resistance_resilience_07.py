import pandas as pd
import numpy as np
import os

# 定义函数 f1 和 f2
def f1(x, gf, n):
    r = x['Plot_ID']
    p = x[n]
    s = gf.loc[r, 'std']
    if s != 0:
        z = (p - gf.loc[r, 'mean']) / s
        return z
    else:
        return 0

def f2(x):
    c = 0
    for i in x:
        if i <= -1:
            c += 1
    return c

# 设置输入和输出文件夹路径
input_folder = r''
output_folder = r''

# 获取所有 .txt 文件路径
input_files = [os.path.join(input_folder, file) for file in os.listdir(input_folder) if file.endswith('.txt')]

# 循环处理每个输入文件
for input_file in input_files:
    # 读取数据
    df = pd.read_csv(input_file, sep='\t')
    # 计算年份范围
    year_range = [2015, 2025]
    # GPP搜索月份
    monthl = [4, 5, 6, 7, 8, 9, 10, 11]
    # 月份为中心的几个月范围内
    window_m = 3
    # 确定Zy年最值方向
    flag1 = 'min'
    # 干旱年间Zy年 <= -1的年份方向
    flag2 = 'min'
    # 多月范围内GGP的Ye 最值方向
    flag3 = 'min'
    # 干旱年份前后三年间Ypre和Ypos的最值方向
    flag4 = 'max'
    # 确定变量名1
    varn = 'PDSI'
    # 确定变量名2
    varn2 = 'gpp'

    # 数据处理和计算部分保持不变
    df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]
    df.sort_values(['Plot_ID', 'Year', 'Month'], inplace=True)
    n1 = f'{varn}_{flag1}'
    gf1 = df.groupby(['Plot_ID', 'Year'], as_index=False)[varn].agg({n1: flag1})
    gf2 = gf1.groupby(['Plot_ID'], as_index=False)[n1].agg(['mean', np.std])
    n2 = f'Z_{varn}'
    gf1[n2] = gf1.apply(lambda x: f1(x, gf2, n1), axis=1)
    sf1 = gf1[gf1[n2] <= -1]
    sf1.to_csv(os.path.join(output_folder, f'{os.path.basename(input_file)[:-4]}_drought_year.txt'), sep='\t', index=False)
    gf3 = gf1.groupby(['Plot_ID'], as_index=False)[n2].agg({f'{n2}_mean': np.mean, f'{n2}(-1)': f2})
    gf3.to_csv(os.path.join(output_folder, f'{os.path.basename(input_file)[:-4]}_{n2}(mean_-1).txt'), sep='\t', index=False)

    ggf = df.groupby(['Plot_ID'])
    rial = []
    riel = []
    missing_GPP = []
    Ye_list = []
    Ypre_list = []
    Ypost_list = []
    wm = int((window_m - 1) / 2)

    for ind, row in sf1.iterrows():
        ID = row['Plot_ID']
        year = int(row['Year'])
        tgf = ggf.get_group(ID)
        tgf = tgf[(tgf['Month'].isin(monthl))]
        tgfy = tgf[(tgf['Year'] == year)].copy()
        indl = tgfy.index.tolist()
        if flag2 == 'max':
            ext_ind = tgfy[varn].idxmax()
        else:
            ext_ind = tgfy[varn].idxmin()
        GPPl = []
        for i in range(ext_ind - wm, ext_ind + wm + 1):
            if i in indl:
                GPPl.append(tgfy.loc[i, varn2])
        if flag3 == 'max':
            Ye = max(GPPl)
        else:
            Ye = min(GPPl)
        yearl = tgf['Year'].tolist()
        max_y = max(yearl)
        min_y = min(yearl)
        if max_y == year or min_y == year:
            rial.append('')
            riel.append('')
            missing_GPP.append('Yes')
            Ye_list.append('')
            Ypre_list.append('')
            Ypost_list.append('')
            continue
        Yprel = []
        for i in range(year - 2, year + 1):
            if i in yearl:
                gl = tgf[tgf['Year'] == i][varn2].tolist()
                Yprel += gl
        Ypostl = []
        for i in range(year, year + 3):
            if i in yearl:
                gl = tgf[tgf['Year'] == i][varn2].tolist()
                Ypostl += gl
        if flag4 == 'min':
            Ypost = min(Ypostl)
            Ypre = min(Yprel)
        else:
            Ypost = max(Ypostl)
            Ypre = max(Yprel)
        if Ypre == 0:
            rial.append('')
            riel.append('')
            missing_GPP.append('Yes')
            Ye_list.append('')
            Ypre_list.append('')
            Ypost_list.append('')
            continue
        ria = (Ye - Ypre) / Ypre
        rie = (Ypost - Ypre) / Ypre
        rial.append(ria)
        riel.append(rie)
        missing_GPP.append('No')
        Ye_list.append(Ye)
        Ypre_list.append(Ypre)
        Ypost_list.append(Ypost)

    sf1['resistance'] = rial
    sf1['resilience'] = riel
    sf1['missing_GPP'] = missing_GPP
    sf1['Ye'] = Ye_list
    sf1['Ypre'] = Ypre_list
    sf1['Ypost'] = Ypost_list
    sf1.to_csv(os.path.join(output_folder, f'{os.path.basename(input_file)[:-4]}_resistance_resilience_ssp5.txt'), sep='\t', index=False)
