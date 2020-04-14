#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author:Yicheng Zhang
import pandas as pd
import numpy as np
import re
import sys
import math
import time
import matplotlib.pyplot as plt

class Wind:
    # '''
    # 制定风资源风速规则程序
    # average_wind_speed_h:小时平均风速
    # average_wind_direction_h:小时平均风向
    # average_pressure_h:小时平均气压
    #
    # wind_speed_10m_h:10m高度小时平均风速
    # wind_speed_30m_h:30m高度小时平均风速
    # wind_speed_50m_h:50m高度小时平均风速
    #
    # wind_direction_30m:30m高度风向
    # wind_direction_50m:50m高度风向
    #
    # '''
    # def __init__(self, average_wind_speed_h, average_wind_direction_h, average_pressure_h, wind_speed_10m_h,
    #              wind_speed_30m_h, wind_speed_50m_h, wind_direction_30m, wind_direction_50m):
    #     self.average_wind_speed_h = average_wind_speed_h
    #     self.average_wind_direction_h = average_wind_direction_h
    #     self.average_pressure_h = average_pressure_h
    #
    #     self.wind_speed_10m_h = wind_speed_10m_h
    #     self.wind_speed_30m_h = wind_speed_30m_h
    #     self.wind_speed_50m_h = wind_speed_50m_h
    #
    #     self.wind_direction_30m = wind_direction_30m
    #     self.wind_direction_50m = wind_direction_50m
    #
    #     self.average_wind_speed_number,self.average_wind_speed_err_number = 0,0

    def __init__(self, path):
        self.path = path
        if "xlsx" in path:
            self.filetype = 0
        elif "txt" in path:
            self.filetype = 1

    def check_lines(self):
        if self.filetype == 1:
            n = 0
            f = open(self.path, 'r')
            lines = f.readlines()
            for lines in lines:
                if "Timestamp" in lines:
                    result = n
                n = n + 1;
            print(result)
        return result

    def subString_avg_wsp(self, template):
        rule = r'Anem_(.*?)_Avg_m/s'
        slotList = re.findall(rule, template)
        return slotList

    def subString_SD_wsp(self, template):
        rule = r'Anem_(.*?)_SD_m/s'
        slotList = re.findall(rule, template)
        return slotList

    def subString_Min_wsp(self, template):
        rule = r'Anem_(.*?)_Min_m/s'
        slotList = re.findall(rule, template)
        return slotList

    def subString_Max_wsp(self, template):
        rule = r'Anem_(.*?)_Max_m/s'
        slotList = re.findall(rule, template)
        return slotList

    # 风向
    def subString_Avg_deg(self, template):
        rule = r'Vane_(.*?)_Avg_deg'
        slotList = re.findall(rule, template)
        return slotList

    # 气压
    def subString_Avg_mb(self, template):
        rule = r'Analog_(.*?)_Avg_mb'
        slotList = re.findall(rule, template)
        return slotList

    # 温度
    def subString_Avg_C(self, template):
        rule = r'Analog_(.*?)_Avg_C'
        slotList = re.findall(rule, template)
        return slotList


class WindRules(Wind):

    def __init__(self, df, path):
        super(WindRules, self).__init__(path)
        if "xlsx" in path:
            self.filetype = 0
        elif "txt" in path:
            self.filetype = 1
        self.df = df

        self.df_name_o, self.df_wsp_name_o, self.df_deg_name_o, self.df_pres_name_o, self.df_temp_name_o = [], [], [], [], []
        self.df_wsp_name, self.df_wsp_SD_name, self.df_wsp_Min_name, self.df_wsp_Max_name = [], [], [], []
        self.df_wsp_index, self.df_wsp_SD_index, self.df_wsp_Min_index, self.df_wsp_Max_index = [], [], [], []

        self.df_deg_name, self.df_deg_index = [], []
        self.df_pres_name, self.df_pres_index = [], []
        self.df_temp_name, self.df_temp_index = [], []

        # results
        self.right_df_wsp_h_list, self.err_df_wsp_h_list, self.total_df_wsp_h_list = [], [], []

    def pre_load(self):
        if self.filetype == 0:
            self.df['Date_Time'] = self.df.iloc[:, 0]
        if self.filetype == 1:
            self.df['Date'] = self.df.index
            self.df['Date_Time'] = self.df['Date'].map(str) + " " + self.df['Timestamp'].map(str)


        self.df['Date_Time'] = pd.to_datetime(self.df['Date_Time'], format='%Y-%m-%d %H:%M:%S')
        self.df = self.df.set_index(self.df['Date_Time'])
        self.df = self.df.drop([self.df.columns[0]], axis=1)
        self.df = self.df.drop([self.df.columns[-1]], axis=1).astype(float)
        self.df_h = self.df.resample('60min').mean()
        # print(self.df.iloc[:, 0])
        # 对数据分类
        for index, column in enumerate(self.df_h.columns):
            # 风速
            if "_m/s" in column:
                if "Avg_m/s" in column:
                    [wsp_name] = Wind.subString_avg_wsp(column)
                    self.df_wsp_name_o.append(column)
                    self.df_wsp_name.append(wsp_name)
                    self.df_wsp_index.append(index)
                elif "SD_m/s" in column:
                    [wsp_SD_name] = Wind.subString_SD_wsp(column)
                    self.df_wsp_SD_name.append(wsp_SD_name)
                    self.df_wsp_SD_index.append(index)
                elif "Min_m/s" in column:
                    [wsp_Min_name] = Wind.subString_Min_wsp(column)
                    self.df_wsp_Min_name.append(wsp_Min_name)
                    self.df_wsp_Min_index.append(index)
                elif "Max_m/s" in column:
                    [wsp_Max_name] = Wind.subString_Max_wsp(column)
                    self.df_wsp_Max_name.append(wsp_Max_name)
                    self.df_wsp_Max_index.append(index)
            # 风向
            elif "Avg_deg" in column:
                [deg_name] = Wind.subString_Avg_deg(column)
                self.df_deg_name_o.append(column)
                self.df_deg_name.append(deg_name)
                self.df_deg_index.append(index)

            # 气压
            elif "Avg_mb" in column:
                [pres_name] = Wind.subString_Avg_mb(column)
                self.df_pres_name_o.append(column)
                self.df_pres_name.append(pres_name)
                self.df_pres_index.append(index)
            # 气温
            elif "Avg_C" in column:
                [temp_name] = Wind.subString_Avg_C(column)
                self.df_temp_name_o.append(column)
                self.df_temp_name.append(temp_name)
                self.df_temp_index.append(index)
        # 风速聚类
        self.df_wsp_h = self.df_h.iloc[:, self.df_wsp_index]
        self.df_wsp_SD_h = self.df_h.iloc[:, self.df_wsp_SD_index]
        self.df_wsp_Max_h = self.df_h.iloc[:, self.df_wsp_Max_index]
        self.df_wsp_Min_h = self.df_h.iloc[:, self.df_wsp_Min_index]
        self.df_wsp_h.columns = self.df_wsp_name
        # 风向、温压
        self.df_deg_h = self.df_h.iloc[:, self.df_deg_index]
        self.df_pres_h = self.df_h.iloc[:, self.df_pres_index]
        self.df_temp_h = self.df_h.iloc[:, self.df_temp_index]
        # print("*" * 50)
        # print(self.df_wsp_h.head())
        return self.df, self.df_wsp_h, self.df_temp_h

    def color_wsp_red(self, val):
        if val < 0 or val >= 75:
            color = 'red'
            bg_color = 'yellow'
        else:
            color = 'black'
            bg_color = 'white'
        return 'color: %s;background-color: %s' % (color, bg_color)

    def color_deg_red(self, val):
        if val < 0 or val >= 360:
            color = 'red'
            bg_color = 'yellow'
        else:
            color = 'black'
            bg_color = 'white'
        return 'color: %s;background-color: %s' % (color, bg_color)

    def color_temp_red(self, val, err_df_temp_h_list):
        # print(val['Date_Time'])
        list_result = []
        print(val.head())
        print(val.index.name)
        val_list = val.index.strftime("%Y-%m-%d %H:%M:%S")
        print(err_df_temp_h_list)
        for i in range(0, len(val.index)):
            if val_list[i] in err_df_temp_h_list:
                color = 'red'
                bg_color = 'yellow'
            else:
                color = 'black'
                bg_color = 'white'
            result = 'color: %s;background-color: %s' % (color, bg_color)
            list_result.append(result)
        print(list_result[0])
        return list_result

    # 主要参数合理范围参考值
    def wind_rules(self, df, df_wsp_h, df_temp_h):
        self.df = df
        self.df_o = df
        self.df_wsp_h = df_wsp_h
        self.df_temp_h = df_temp_h
        self.df_name_o = self.df.columns
        # for col_name in self.df_name_o:
        #     if col_name in self.df_wsp_name_o or col_name in self.df_deg_name_o or col_name in self.df_pres_name_o \
        #             or col_name in self.df_temp_name_o:
        #         self.df = self.df.drop([col_name], axis=1)
        print("*" * 250)

        # temperature rules
        # print(self.df_temp_name_o)
        shift_df_temp_h = self.df_temp_h - self.df_temp_h.shift(1)
        err_df_temp_h = shift_df_temp_h.loc[(shift_df_temp_h.iloc[:, 0] < -5) | (shift_df_temp_h.iloc[:, 0] > 5)].index

        err_df_temp_h_list = err_df_temp_h.strftime("%Y-%m-%d %H:%M:%S").tolist()
        print(err_df_temp_h_list)
        self.wind_rules = self.df_o.style.apply(WindRules.color_temp_red, err_df_temp_h_list=err_df_temp_h_list,
                                                subset=self.df_temp_name_o)

        # self.wind_rules = self.df_o.style.applymap(WindRules.color_wsp_red, subset=self.df_wsp_name_o).applymap(
        #     WindRules.color_deg_red, subset=self.df_deg_name_o)
        #
        # print(self.wind_rules)
        writer = pd.ExcelWriter('my.xlsx')
        self.wind_rules.to_excel(writer, float_format='%.5f')
        writer.save()

        #        # wind speed rules
        # for index, column in enumerate(self.df_wsp_h.columns):
        #     right_df_wsp_h = self.df_wsp_h[
        #         (self.df_wsp_h.iloc[:, index] < 75) & (self.df_wsp_h.iloc[:, index] >= 0)]
        #     err_df_wsp_h = self.df_wsp_h[
        #         (self.df_wsp_h.iloc[:, index] >= 75) | (self.df_wsp_h.iloc[:, index] < 0)]
        #     total_df_wsp_h = self.df_wsp_h.iloc[:, index]
        #
        #
        #     self.right_df_wsp_h_list.append(right_df_wsp_h.shape[0])
        #     self.err_df_wsp_h_list.append(err_df_wsp_h.shape[0])
        #     self.total_df_wsp_h_list.append(total_df_wsp_h.shape[0])

        print("*" * 50)
        # print(self.right_df_wsp_h_list)
        # print(self.err_df_wsp_h_list)
        # print(self.total_df_wsp_h_list)




class WindPower(Wind):
    def __init__(self, df, path):
        super(WindPower, self).__init__(path)
        if "xlsx" in path:
            self.filetype = 0
        elif "txt" in path:
            self.filetype = 1
        self.df = df

    def pre_load_power_data(self):
        # print(self.df['Date/Time'])
   
        self.df['Date_Time'] = pd.to_datetime(self.df['Date/Time'], format='%d %m %Y %H:%M')
        self.df = self.df.set_index(self.df['Date_Time'])
        self.df = self.df.drop([self.df.columns[0]], axis=1)
        self.df = self.df.drop([self.df.columns[-1]], axis=1).astype(float)
        return self.df
    


    def windspeed_label(self,df):
        self.df=df
        wind_label_bin=[0]
        wind_label_list=[0]
        i=0.25
        while i<=25.5:
            wind_label_bin.append(i)
            wind_label_list.append(i+0.25)
            i+=0.5
        del(wind_label_list[-1])
        self.df['wind_label_bin']=pd.cut(self.df['Wind Speed (m/s)'],wind_label_bin,labels=wind_label_list)
        self.df['month']=df.index.month
        df_pivot_windspeed=pd.pivot_table(self.df,index=['month','wind_label_bin'],values=['LV ActivePower (kW)','Wind Speed (m/s)','Wind Direction (°)']
        ,aggfunc={'LV ActivePower (kW)':np.mean,'Wind Speed (m/s)':np.mean})
        return df_pivot_windspeed




if __name__ == "__main__":
    path = './wind-turbine-scada-dataset/T1.csv'
    df = pd.read_csv(path)
    WindPower=WindPower(df,path)
    df=WindPower.pre_load_power_data()

    # df=df[df.index.month==1]
    df_pivot_windspeed=WindPower.windspeed_label(df)

  
    df_pivot=df_pivot_windspeed.loc[pd.IndexSlice[4:5,3:],:]#第一个是月份，第二个变量是风速标签
    print(df_pivot)
    plt.scatter(x=df_pivot['Wind Speed (m/s)'],y=df_pivot['LV ActivePower (kW)'],color='DarkBlue',label='Class1')
    plt.show()

