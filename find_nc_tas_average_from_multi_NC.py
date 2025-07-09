from netCDF4 import Dataset,num2date
import pandas as pd
import os
def near_ind(df,name,extreme,name_list):
    ##缩小经纬度的范围
    if extreme=='min':
        v = df[name].min()
        near_v = min(name_list, key=lambda x: (abs(x - v), x))
        return name_list.index(near_v)-1
    elif extreme=='max':
        v = df[name].max()
        near_v = min(name_list, key=lambda x: (abs(x - v), x))
        return name_list.index(near_v)+2
# 读取location文件
df = pd.read_excel(r'')
#NC文件存放的文件夹
dir_path = r''
fn = os.listdir(dir_path)
# 保存的文件夹
save_dir = r''
#时间跨度
year1 = [2015,2100]
ym = []
for i in range(year1[0],year1[1]+1):
    for j in range(1,13):
        ym.append((i,j))
#变量名
var='tas'
ef = ''
#遍历NC文件
for w in fn:
    if '.nc' not in w:
        continue
    # 查看nc数据
    nc_obj = Dataset(dir_path+'\\'+w)
    # 获取维度范围
    lat_list = list(nc_obj.variables['lat'])
    # 获取经度范围
    lon_list = list(nc_obj.variables['lon'])

    lon_list_t = [i -180 for i in lon_list]
    min_lat = near_ind(df,'Latitude','min',lat_list)
    max_lat = near_ind(df,'Latitude','max',lat_list)
    min_lon = near_ind(df,'Longitude','min',lon_list_t)
    max_lon = near_ind(df,'Longitude','max',lon_list_t)
    # 缩小维度范围
    lat_list = lat_list[min_lat:max_lat]
    # 缩小经度范围
    lon_list = lon_list[min_lon:max_lon]
    #获取时间列表
    time1 = nc_obj.variables['time'][:]
    time_unit = nc_obj.variables["time"].getncattr('units')
    time_cal = nc_obj.variables["time"].getncattr('calendar')
    local_time = num2date(time1, units=time_unit, calendar=time_cal)
    #获取时间列表的年和月
    local_time = [(y.year, y.month) for y in local_time]
    ind_t = []
    con_t = []
    #提取共同的年和月
    for ind,e in enumerate(local_time):
        if e in ym:
            ind_t.append(ind)
            con_t.append(e)
    #提取变量维度
    #有气压下 通过(用NC软件（Panoply,exe）查看变量是否受除时间和经纬度以外其他纬度参数(如汽压plev)影响)
    #var_f = nc_obj.variables[var][ind_t, 18:19, min_lat:max_lat, min_lon:max_lon]
    #无气压下
    var_f = nc_obj.variables[var][ind_t, min_lat:max_lat, min_lon:max_lon]
    # 记录上次的索引号
    last_lat= 0
    last_lon = 0
    year_l = []
    month_l = []
    for k,v in con_t:
        year_l.append(k)
        month_l.append(v)
    tf = ''
    # 逐行读取点
    a = 0
    ID_l = []
    year_ll = []
    month_ll = []
    var_ll = []
    t_var = []
    for index, row in df.iterrows():
        a+=1
        print(a)
        # 获取维度
        lat = row['Latitude']
        # 获取经度
        lon = row['Longitude']+180
        min_lat = min(lat_list, key=lambda x: (abs(x -lat), x))
        min_lon = min(lon_list, key=lambda x: (abs(x - lon), x))
        # 获取最近的标记点
        lat_ind = lat_list.index(min_lat)
        lon_ind = lon_list.index(min_lon)
        t_ID = row['OrdW']
        ID_l += [t_ID for i in range(len(ind_t))]
        # 获取空气温度数据
        if last_lat!=lat_ind or last_lon!=lon_ind:
            #有气压下
            #t_var = var_f[:, 0, lat_ind, lon_ind]
            #无气压下
            t_var = var_f[:,  lat_ind, lon_ind]  #无气压下
            t_var = t_var.tolist()
            t_var = [round(i, 2) for i in t_var]
            last_lat=lat_ind
            last_lon=lon_ind
        year_ll += year_l
        month_ll += month_l
        var_ll += t_var
    # 保存数据
    sf = pd.DataFrame({'OrdW':ID_l ,'Stimu_year':year_ll, 'Month':month_ll, var:var_ll})
    #对每个nc文件提取结果合并
    if len(ef)==0:
        ef = sf
    else:
        ef=ef.append(sf,ignore_index=True)
#分组求平均
gf = ef.groupby(['OrdW','Stimu_year','Month'],as_index=False).agg({var:['mean','std']})
gf.columns = ['OrdW','Stimu_year','Month','mean','std']
#保存结果
gf.to_csv(save_dir +'\\'+ var+'_NC_tas_mean_SSP5.txt', sep='\t', index=False)
