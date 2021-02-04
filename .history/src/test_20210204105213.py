#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   easy-money.py
@Time    :   2021/02/04 09:03:02
@Author  :   Jiajun Chen 
@Version :   1.0
@Contact :   554001000@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
'''

# 东方财富网 首发申报及上会信息


import re
import pickle
from datetime import datetime, timedelta
from urllib.parse import urlencode
import pandas as pd
import requests
import re
import time
from bs4 import BeautifulSoup
import configparser
import os.path
import csv

base_url = 'https://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?'
headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
zzsc_csv_path = './data/EastMoney/eastmoney_zzsc.csv'
zzsc_pkl_path = './saved_config/eastmoney_zzsc.pkl'

def update_date():
    '''
    获取最新更新日期
    '''
    r = requests.get('http://data.eastmoney.com/xg/xg/sbqy.html',
                        headers=headers)
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text, 'html.parser')
    newDate = soup.find('option').get_text()
    return newDate


def dateList_gen():
    '''
    fetch all existing date_data
    '''
    r = requests.get('http://data.eastmoney.com/xg/xg/sbqy.html',
                     headers=headers)
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text, 'html.parser')

    dateList = [i.text for i in soup.findAll('option')]
    return dateList


def update_eastmoneyData():
    # 如果文件存在，执行更新
    # newDate = update_date()
    dataList = dateList_gen()
    if not os.path.isfile('./data/EastMoney/eastmoneyRawData.csv'):
        columns = ['机构名称', '类型', '板块', '注册地', '保荐机构', '保荐代表人', '律师事务所', '签字律师', '会计师事务所',
        '签字会计师', '是否提交财务自查报告', '所属行业', '日期', 'xxx', '时间戳', '简称', '文件链接']
        with open('./data/EastMoney/eastmoneyRawData.csv','w') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
    for date in reversed(dataList):
        if not os.path.isfile('./data/EastMoney/首发信息/{}.csv'.format(date)):
            print('find new date：{}, fetching.....'.format(date))
            df =get_eastmoneyData(date)
            df.to_csv('./data/EastMoney/eastmoneyRawData.csv', mode='a', header=False,index=False,encoding='utf-8-sig')

    return 


def get_eastmoneyData(date):
    query = {'type': 'NS',
        'sty': 'NSFR',
        'st': '1',
        'sr': '-1',
        'p': '1',
        'ps': '5000',
        'js': 'var IBhynDx={pages:(pc),data:[(x)]}',
        'mkt': '1',
        'fd' : date,
        'rt': '53721774'
    }

    rs = requests.get(base_url, params=query, headers=headers)
    js = rs.text.split('var IBhynDx={pages:1,data:')[1]
    data = eval(js[:-1])
    temp = [i.split(',') for i in data]
    columns = [
        '会计师事务所', '保荐代表人', '保荐机构', 'xxx', '律师事务所', '日期', '所属行业', '板块',
        '是否提交财务自查报告', '注册地', '类型', '机构名称', '签字会计师', '签字律师', '时间戳', '简称'
    ]
    df = pd.DataFrame(temp, columns=columns)
    df['文件链接'] = df['时间戳'].apply(
        lambda x: "https://notice.eastmoney.com/pdffile/web/H2_" + x + "_1.pdf"
    )
    df = df[[
        '机构名称', '类型', '板块', '注册地', '保荐机构', '保荐代表人', '律师事务所', '签字律师', '会计师事务所',
        '签字会计师', '是否提交财务自查报告', '所属行业', '日期', 'xxx', '时间戳', '简称', '文件链接'
    ]]
    df = df[df['板块'] != '创业板']
    df.replace({'是否提交财务自查报告': ' '}, '是')
    df.replace({'是否提交财务自查报告': '不适用'}, '是')
    df['机构名称'] = df['机构名称'].replace(r'\*', '', regex=True)
    df['机构名称'] = df['机构名称'].replace(r'股份有限公司', '', regex=True)

    df.to_csv('C:/Users/chen/Desktop/IPO_info/data/EastMoney/首发信息/{}.csv'.format(date),index=False, encoding='utf-8-sig')
    return df

def update_zzscData():
    
    newDate = update_date()
    if newDate != lastDate:
        try:
            zzsc_dict = load_pickle(zzsc_pkl_path)
            data = get_zzscData(newDate)

            for i in data:
                name = i.split(',')[1]
                if name not in zzsc_dict:
                    zzsc_dict[name] = i.split(',')[2]
                else:
                    continue
        except:
            zzsc_dict = gen_zzscDict()
        else:
            zzsc_df = pd.DataFrame(zzsc_dict.items(), columns=['机构名称', '决定终止审查时间'])
            zzsc_df['机构名称'] = zzsc_df['机构名称'].replace(r'\*', '', regex=True)
            zzsc_df['机构名称'] = zzsc_df['机构名称'].replace(r'股份有限公司', '', regex=True)
            zzsc_df['机构名称'] = zzsc_df['机构名称'].replace(r'\(', '（', regex=True)
            zzsc_df['机构名称'] = zzsc_df['机构名称'].replace(r'\)', '）', regex=True)
            zzsc_df.to_csv(zzsc_csv_path,
                        encoding='utf-8-sig',
                        index=False)
            save_pickle(zzsc_dict,zzsc_pkl_path)
    return zzsc_df


def gen_zzscDict():
    dateList = gen_datalist()
    zzsc_dict = {}
    for date in dateList:
        data = get_zzscData(date)
        for i in data:
            name = i.split(',')[1]
            if name not in zzsc_dict:
                zzsc_dict[name] = i.split(',')[2]
            else:
                continue
    save_pickle(zzsc_dict,zzsc_pkl_path)
    return zzsc_dict

def get_zzscData(date):
    query = {
        'type': 'NS',
        'sty': 'NSSE',
        'st': '1',
        'sr': '-1',
        'p': '1',
        'ps': '500',
        'js': 'var IBhynDx={pages:(pc),data:[(x)]}',
        'mkt': '4',
        'stat': 'zzsc',
        'fd': date,
        'rt': '53727636'
    }

    url = base_url + urlencode(query)
    rss = requests.get(url, headers=headers)
    if rss.text == 'var IBhynDx={pages:0,data:[{stats:false}]}':
        return ''
    jss = rss.text.split('var IBhynDx={pages:1,data:')[1]
    data = eval(jss[:-1])

    return data


if __name__ == '__main__':
    update_eastmoneyData()