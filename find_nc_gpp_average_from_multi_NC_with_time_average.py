
from netCDF4 import Dataset,num2date
import pandas as pd
import os
import datetime
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

def avg_multi(fnt,dir_path,save_dir,var,year1,time_dim,stats_l,month_y):
    # 读取location文件
    if '.xlsx' in fnt:
        # 读取location文件
        df = pd.read_excel(fnt)
    else:
        df = pd.read_csv(fnt, sep='\t')
    #NC文件存放的文件夹
    fn = os.listdir(dir_path)
    #时间跨度
    ym = []
    if time_dim == 'year':
        for i in range(year1[0], year1[1] + 1):
            ym.append(i)
    elif time_dim == 'month':
        for i in range(year1[0], year1[1] + 1):
            for j in range(1, 13):
                ym.append((i, j))
    elif time_dim=='multi_month':
        for i in range(year1[0], year1[1] + 1):
            for j in month_y:
                ym.append((i, j))
    else:
        ##开始时间
        start_date = datetime.date(year1[0], 1, 1)
        # 结束时间
        end_date = datetime.date(year1[1], 12, 31)
        # 获取时间列表
        date_range = range(0, (end_date - start_date).days + 1, 1)
        date_list = [start_date + datetime.timedelta(days=x) for x in date_range]
        ym = [(x.year, x.month, x.day) for x in date_list]


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
        # 获取时间列表的年和月
        if time_dim == 'year':
            local_time = [(y.year) for y in local_time]
        elif time_dim in ['month','multi_month']:
            local_time = [(y.year, y.month) for y in local_time]
        else:
            local_time = [(y.year, y.month, y.day) for y in local_time]
        ind_t = []
        con_t = []
        #提取共同的年和月
        for ind,e in enumerate(local_time):
            if e in ym:
                if time_dim!='multi_month':
                    ind_t.append(ind)
                    con_t.append(e)
                else:
                    ind_t.append(ind)
                    con_t.append(str((e[0],month_y)))
        #提取变量维度
        #有气压下 通过(用NC软件（Panoply,exe）查看变量是否受除时间和经纬度以外其他纬度参数(如汽压plev)影响)
        #var_f = nc_obj.variables[var][ind_t, 18:19, min_lat:max_lat, min_lon:max_lon]
        #无气压下
        var_f = nc_obj.variables[var][ind_t, min_lat:max_lat, min_lon:max_lon]
        # 记录上次的索引号
        last_lat= 0
        last_lon = 0
        tf = ''
        # 逐行读取点
        a = 0
        ID_l = []
        time_ll = []
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
            t_ID = row['Plot_ID']
            ID_l += [t_ID for i in range(len(ind_t))]
            # 获取空气温度数据
            if last_lat!=lat_ind or last_lon!=lon_ind:
                #有气压下
                #t_var = var_f[:, 0, lat_ind, lon_ind]
                #无气压下
                t_var = var_f[:,  lat_ind, lon_ind]  #无气压下
                t_var = t_var.tolist()
                # t_vart= []
                # for tt in t_var:
                #     if tt!=None:
                #         t_vart.append(round(tt,2))
                #     else:
                #         t_vart.append('')
                # t_var=t_vart
                last_lat=lat_ind
                last_lon=lon_ind
            time_ll += con_t
            var_ll += t_var
        # 保存数据
        sf = pd.DataFrame({'Plot_ID':ID_l ,'time':time_ll, var:var_ll})
        #对每个nc文件提取结果合并
        if len(ef)==0:
            ef = sf
        else:
            ef=ef.append(sf,ignore_index=True)
    #分组求平均
    gf = ef.groupby(['Plot_ID','time'],as_index=False).agg({var:stats_l})
    gf.columns = ['Plot_ID','time']+stats_l
    #保存结果
    gf.to_csv(save_dir +'\\'+ var+'_NC_gpp_test_time_average_multi_month.txt', sep='\t', index=False)


if __name__ == '__main__':
    # 读取location文件
    fnt = r' .xlsx'
    # NC文件存放的文件夹
    dir_path = r' '
    # 保存的文件夹
    save_dir = r' '
    # 变量名
    var = 'gpp'
    # 时间跨度
    year1 = [2020, 2100]
    #如果有月份要求，则填入对应的月份,下面行的time_dim填为multi-month.time_dim填写day,month以及year时month_y应该不起作用
    month_y = [3,4,5,6,7,8,9,10]
    #时间维度（年、月、日）可输入day\month\year,查看前面的函数对应进行填写
    #time_dim = 'month'
    time_dim = 'month'
    #指标
    stats_l = ['mean']
    avg_multi(fnt,dir_path,save_dir,var,year1,time_dim,stats_l,month_y )