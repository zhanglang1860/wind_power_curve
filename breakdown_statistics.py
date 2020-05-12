#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author:Yicheng Zhang
import pandas as pd
import re
import sys
import math
import time
import xlrd

def read_file(fpath, sheet_names):
    dfList=[]
    for sheet_name in sheet_names:
        print(sheet_name)
        data =pd.read_excel(fpath, sheet_name=sheet_name,usecols=['ID','单元','事件时间','类型','事件号','值','描述','注释'])
        data.reset_index()
        dfList.append(data)

    dfs = pd.concat(dfList, axis=0)
    return dfs

def statistics_method(df_stat):
    j=0
    k=0
    for i in range(df_stat.shape[0]):
        if i>=k:
            if df_stat['值'].iloc[i]=='关闭':
                pass
            elif df_stat['值'].iloc[i]=='开始':
                
                for j in range(i+1,df_stat.shape[0]):
                    if (df_stat['事件号'].iloc[i]== df_stat['事件号'].iloc[j]) and (df_stat['值'].iloc[j]=='关闭'):
                        df_stat['注释'].iloc[i]='yellow'
                        df_stat['注释'].iloc[j]='yellow'
                        break
                    else:
                        df_stat['注释'].iloc[j]='blue'
            k=j+1

    return df_stat

if __name__ == "__main__":
    fpath = r'D:\onedrive_data\OneDrive - Platinum\中央研究院_任务\04 测风数据处（风机运行数据）\代码测试\风机故障统计表-编程.xlsx'
    fpath2 = r'D:\onedrive_data\OneDrive - Platinum\中央研究院_任务\04 测风数据处（风机运行数据）\代码测试\风机故障统计表-编程1.xlsx'
 
    xls = xlrd.open_workbook(fpath, on_demand=True)
    df = read_file(fpath, xls.sheet_names())
    # print(df['描述'].iloc[2958:2962])

    df_stat=df[(df['类型']=='故障1') | (df['类型']=='故障2')]
    print(df_stat.head())
    df_stat.reset_index(drop=True, inplace=True)
    print(df_stat.shape)
    print(df_stat.tail())
    
    df_stat=statistics_method(df_stat)
    df_stat_result=df_stat[(df_stat['注释']=='yellow') & (df_stat['值']=='开始')]
    df_stat_result_group = df_stat_result.groupby('描述')['注释'].count().sort_values(ascending=False)
    # 打开excel
    writer = pd.ExcelWriter(fpath2)
    df.to_excel(excel_writer=writer)
    df_stat.to_excel(excel_writer=writer, sheet_name='统计')
    df_stat_result_group.to_excel(excel_writer=writer, sheet_name='结果')
    # 保存writer中的数据至excel
    # 如果省略该语句，则数据不会写入到上边创建的excel文件中
    writer.save()


