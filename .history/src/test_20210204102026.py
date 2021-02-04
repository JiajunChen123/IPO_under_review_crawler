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
# def update_date():
#     '''
#     获取最新更新日期
#     '''
#     r = requests.get('http://data.eastmoney.com/xg/xg/sbqy.html',
#                         headers=headers)
#     r.encoding = 'gbk'
#     soup = BeautifulSoup(r.text, 'html.parser')
#     newDate = soup.find('option').get_text()
#     return newDate


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
        with open('./data/EastMoney/{eastmoneyRawData}.csv','w') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
    for date in reversed(dataList):
        if not os.path.isfile('./data/EastMoney/首发信息/{}.csv'.format(date)):
            print('fetching date: ',date)
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
        # start = datetime.strptime('2017-01-05','%Y-%m-%d').date()
        # while start < datetime.today().date():
        #     query['fd'] = start
        # url = base_url + urlencode(query)
        # print(url)
        # yield url
        # start += timedelta(days=7)
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


if __name__ == '__main__':
    update_eastmoneyData()