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
from utils import save_pickle,load_pickle

# config = configparser.ConfigParser()
# config.read('./src/Config.ini')
# # headers = config['eastmoney']['headers']
# base_url = config['eastmoney']['base_url']
base_url = 'https://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?'
lastDate = '2021-1-21'
eastmoney_raw_data_path = './data/EastMoney/eastmoney_raw_data.csv'
zzsc_csv_path = './data/EastMoney/eastmoney_zzsc.csv'
zzsc_pkl_path = './saved_config/eastmoney_zzsc.pkl'
szzxb_stocksInfo_path = './saved_config/szzxb_stocksInfo.pkl'
shzb_stocksInfo_path = './saved_config/shzb_stocksInfo.pkl'
zb_zxb_stocksInfo_path = './saved_config/zb_zxb_stocksInfo.pkl'
eastmoney_meeting_path = './data/EastMoney/eastmoney_data_meeting.csv'
headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}

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
    dateList = dateList_gen()
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

def get_meetingData(newDate):
    if newDate != lastDate or not os.path.isfile(eastmoney_meeting_path):
        meetingInfo = []
        for marketType in ['2', '4']:  # 2 为主板， 4 为中小板
            query = {
                'type': 'NS',
                'sty': 'NSSH',
                'st': '1',
                'sr': '-1',
                'p': '1',
                'ps': '5000',
                'js': 'var IBhynDx={pages:(pc),data:[(x)]}',
                'mkt': marketType,
                'rt': '53723990'
            }

            url = base_url + urlencode(query)
            rss = requests.get(url, headers=headers)
            jss = rss.text.split('var IBhynDx={pages:1,data:')[1]
            data = eval(jss[:-1])
            meetingInfo.extend(data)
        temp = [j.split(',') for j in meetingInfo]
        columns = [
            '时间戳', 'yyy', '公司代码', '机构名称', '详情链接', '申报日期', '上会日期', '申购日期', '上市日期',
            '9', '拟发行数量', '发行前总股本', '发行后总股本', '13', '占发行后总股本比例', '当前状态', '上市地点',
            '主承销商', '承销方式', '发审委委员', '网站', '简称'
        ]
        df = pd.DataFrame(temp, columns=columns)
        df['文件链接'] = df['时间戳'].apply(
            lambda x: "https://notice.eastmoney.com/pdffile/web/H2_" + x + "_1.pdf"
        )
        df['详情链接'] = df['公司代码'].apply(
            lambda x: "data.eastmoney.com/xg/gh/detail/" + x + ".html")
        df = df[[
            '机构名称', '当前状态', '上市地点', '拟发行数量', '申报日期', '上会日期', '申购日期', '上市日期',
            '主承销商', '承销方式', '9', '发行前总股本', '发行后总股本', '13', '占发行后总股本比例', '发审委委员',
            '网站', '公司代码', 'yyy', '时间戳', '简称', '详情链接', '文件链接'
        ]]
        df['机构名称'] = df['机构名称'].replace(r'\*', '', regex=True)
        df['机构名称'] = df['机构名称'].replace(r'股份有限公司', '', regex=True)
        df['机构名称'] = df['机构名称'].replace(r'\(', '（', regex=True)
        df['机构名称'] = df['机构名称'].replace(r'\)', '）', regex=True)
        df.to_csv(
            eastmoney_meeting_path,
            index=False,
            encoding='utf-8-sig')
    else:
        df = pd.read_csv(eastmoney_meeting_path,keep_default_na=False)
    return df


def eastmoney_cleanUP():
    east_money = pd.read_csv(eastmoney_raw_data_path, keep_default_na=False)
    east_money.replace({'是否提交财务自查报告': ' '}, '是')
    east_money.replace({'是否提交财务自查报告': '不适用'}, '是')
    east_money['机构名称'] = east_money['机构名称'].replace(r'\*', '', regex=True)
    east_money['机构名称'] = east_money['机构名称'].replace(r'股份有限公司', '', regex=True)
    east_money['机构名称'] = east_money['机构名称'].replace(r'\(', '（', regex=True)
    east_money['机构名称'] = east_money['机构名称'].replace(r'\)', '）', regex=True)
    east_money = east_money[east_money['板块'] != '创业板']
    east_money['类型'] = pd.Categorical(east_money['类型'], 
                      categories=["已受理","已反馈","预先披露更新","中止审查","已提交发审会讨论，暂缓表决",
                     "已上发审会，暂缓表决","已通过发审会"],ordered=True)
    east_money.sort_values(['机构名称','保荐机构','类型','日期'], inplace=True)
    # east_money.to_csv('./pre_cleab.csv',encoding='utf-8-sig',index=False)
    east_money.drop_duplicates(subset=['机构名称','保荐机构', '类型',],
                               keep='first',
                               inplace=True)
    east_money.to_csv(
        './data/EastMoney/eastmoney_data_cleaned_v2.csv',
        encoding='utf-8-sig',
        index=False)
    return east_money


def gen_finalData(cleaned_easymoney_df, meetingInfo_df, zzsc_df):
    '''
         主板、中小板 = {'机构名称':'',
                        '简称':'',
                        'Wind代码':'',
                        '统一社会信用代码':'',
                        '板块':'',
                        '注册地':'',
                        '所属行业':'',
                        '经营范围':'',
                        '预先披露':'[日期]',
                        '已反馈':'[日期]',
                        '预先披露更新':'[日期]',
                        '发审会':{'中止审查':'[日期]',
                                  '已上发审会，暂缓表决':'[日期]',
                                  '已提交发审会讨论，暂缓表决:'[日期]',
                                  '已通过发审会':'[日期]'},
                        '终止审查':'[日期]',
                        '上市日期':'[日期]',
                        '保荐机构':'',
                        '律师事务所':,
                        '会计师事务所':'',
                        '发行信息':{'拟发行数量':'',
                                    '发行前总股本':'',
                                    '发行后总股本':''},                        
                        '反馈文件'：'[链接]'
                    }  
    '''
    all_data = {}  # 总数据

    ekk = cleaned_easymoney_df.values.tolist()

    for i in ekk:
        i
        if i[0] not in all_data:
            all_data[i[0]] = {
                '机构名称': i[0] + '股份有限公司',
                '简称': i[15],
                'Wind代码': '',
                '统一社会信用代码': '',
                '板块': i[2],
                '注册地': '',
                '所属行业': '',
                '经营范围': '',
                '预先披露': '',
                '已反馈': '',
                '预先披露更新': '',
                '发审会': {
                    '中止审查': '',
                    '已上发审会，暂缓表决': '',
                    '已提交发审会讨论，暂缓表决': '',
                    '已通过发审会': ''
                },
                '终止审查': '',
                '上市日期': '',
                '保荐机构': i[4],
                '保荐代表人': '',
                '律师事务所': i[6],
                '签字律师': '',
                '会计师事务所': i[8],
                '签字会计师': '',
                '发行信息': {
                    '拟发行数量（万）': '',
                    '发行前总股本（万）': '',
                    '发行后总股本（万）': ''
                },
                '反馈文件': ''
            }

        if i[1] == '已受理':
            all_data[i[0]]['预先披露'] = i[12]
        elif i[1] == '已反馈':
            all_data[i[0]]['已反馈'] = i[12]
        elif i[1] == '预先披露更新':
            all_data[i[0]]['预先披露更新'] = i[12]
        elif i[1] == '已通过发审会':
            all_data[i[0]]['发审会']['已通过发审会'] = i[12]
        elif i[1] == '已提交发审会讨论，暂缓表决':
            all_data[i[0]]['发审会']['已提交发审会讨论，暂缓表决'] = i[12]
        elif i[1] == '已上发审会，暂缓表决':
            all_data[i[0]]['发审会']['已上发审会，暂缓表决'] = i[12]
        elif i[1] == '中止审查':
            all_data[i[0]]['发审会']['中止审查'] = i[12]

        if all_data[i[0]]['注册地'] == '' and i[3] != '':
            all_data[i[0]]['注册地'] = i[3]
        if all_data[i[0]]['所属行业'] == '' and i[11] != '':
            all_data[i[0]]['所属行业'] = i[11]

        if all_data[i[0]]['保荐代表人'] == '' and i[5] != '':
            all_data[i[0]]['保荐代表人'] = i[5]
        if all_data[i[0]]['签字律师'] == '' and i[7] != '':
            all_data[i[0]]['签字律师'] = i[7]
        if all_data[i[0]]['签字会计师'] == '' and i[9] != '':
            all_data[i[0]]['签字会计师'] = i[9]

    # 添加上会信息
    ekk2 = meetingInfo_df.values.tolist()
    error_set = {}
    for i in ekk2:
        i[0] = i[0].replace(r'股份有限公司', '')

        if i[0] not in all_data:
            print("Error: Cannot find ", i[0])
            error_set.update({i[0]: i[5]})
            continue
        if i[1] == '上会未通过':
            all_data[i[0]]['发审会']['上会未通过'] = i[5]
        elif i[1] == '取消审核':
            all_data[i[0]]['发审会']['取消审核'] = i[5]
        elif i[1] == '上会通过':
            all_data[i[0]]['发审会']['已通过发审会'] = i[5]

        if i[7] != '':
            all_data[i[0]]['上市时间'] = i[7]

        all_data[i[0]]['发行信息']['拟发行数量'] = "{:.2f}".format(int(i[3]) / 10000)
        all_data[i[0]]['发行信息']['发行前总股本'] = "{:.2f}".format(int(i[11]) / 10000)
        all_data[i[0]]['发行信息']['发行后总股本'] = "{:.2f}".format(int(i[12]) / 10000)

    # 添加终止审查信息
    ekk3 = zzsc_df.values.tolist()

    for i in ekk3:
        name = i[0].replace(r'股份有限公司', '')
        if name not in all_data:
            print("Error: Cannot find in zzsc", i[0])
            error_set.update({name: i[1]})
            continue
        all_data[name]['终止审查'] = i[1]


    save_pickle(all_data, zb_zxb_stocksInfo_path)

    return all_data
# def update_all():
#     try:
#         with open('','rb') as file:
#             zb_zxb_dict = pickle.load(file)
#         _,temp = update_eastmoneyData()
#         for i in temp:
#             if i not in zb_zxb_dict:
#                 pass
#             else:
#             #     columns = [
#             #     '会计师事务所', '保荐代表人', '保荐机构', 'xxx', '律师事务所', '日期', '所属行业', '板块',
#             #     '是否提交财务自查报告', '注册地', '类型', '机构名称', '签字会计师', '签字律师', '时间戳', '简称'
#             # ]
#                 i[]


def update_stockInfo(df):
    try:
        allStocksInfo = load_pickle(zb_zxb_stocksInfo_path)
    except:
        east_money_df = eastmoney_cleanUP()
        meetingInfo_df = get_meetingData()
        zzsc_df = update_zzscData()
        allStocksInfo = gen_finalData(east_money_df,meetingInfo_df,zzsc_df) 
    else:
        for index, row in df.iterrows():
            if allStocksInfo[row['机构名称']][row['类型']]

if __name__ == '__main__':
    # newDate = update_date()
    # # update_eastmoneyData(newDate)
    # east_money_df = eastmoney_cleanUP()
    # meetingInfo_df = get_meetingData(newDate)
    # zzsc_df = update_zzscData(newDate)
    # # dateList = date_gen()
    # # get_eastmoneyData(dateList)
    # # east_money_df = eastmoney_cleanUP()
    # # east_money_df =  pd.read_csv('./EastMoney/easymoney_data_new.csv',keep_default_na=False)
    # # meetingInfo_df = pd.read_csv('./EastMoney/eastmoney_data_meeting.csv',keep_default_na=False)
    # # meetingInfo_df = get_meetingData()
    # # zzsc_df = pd.read_csv('./EastMoney/zzsc.csv')
    # all_data,_,_ = gen_finalData(east_money_df,meetingInfo_df,zzsc_df) 
    # print('Complete!')
    eastmoney_cleanUP()