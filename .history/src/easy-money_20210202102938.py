#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 东方财富网 首发申报


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
from pathlib import Path


config = configparser.ConfigParser()
config.read('Config.ini')
headers = config['eastmoney']['headers']
base_url = config['eastmoney']['base_url']


def dateList_gen():
    r = requests.get('http://data.eastmoney.com/xg/xg/sbqy.html',
                     headers=headers)
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text, 'html.parser')

    dateList = [i.text for i in soup.findAll('option')]
    yield dateList

def update_date():
    r = requests.get('http://data.eastmoney.com/xg/xg/sbqy.html',
                        headers=headers)
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text, 'html.parser')
    newDate = soup.find('option').get_text()
    return newDate


def update_eastmoneyData(newDate):

    eastmoney_raw_data = Path(config['eastmoney']['raw_data'])
    # 如果文件存在，执行更新
    if eastmoney_raw_data.is_file():
        # newDate = update_date()
        # 如果有更新
        if newDate != config['eastmoney']['lastDate']:
            query = {
            'type': 'NS',
            'sty': 'NSFR',
            'st': '1',
            'sr': '-1',
            'p': '1',
            'ps': '5000',
            'js': 'var IBhynDx={pages:(pc),data:[(x)]}',
            'mkt': '1',
            'fd': newDate,
            'rt': '53721774'
        }

            url = base_url + urlencode(query)

            rs = requests.get(url, headers=headers)
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

            df.to_csv(
                'C:/Users/chen/Desktop/IPO_info/EastMoney/eastmoney_raw_data.csv',mode='a',
                index=False, header=False, encoding='utf-8-sig')
            return df
    else:
        dateList = dateList_gen()
        get_eastmoneyData(dateList)
        return df

def get_eastmoneyData(dateList):
    query = {
        'type': 'NS',
        'sty': 'NSFR',
        'st': '1',
        'sr': '-1',
        'p': '1',
        'ps': '5000',
        'js': 'var IBhynDx={pages:(pc),data:[(x)]}',
        'mkt': '1',
        'rt': '53721774'
    }
    main_data = []
    for date in dateList:
        print('fetching date: ',date)
        query['fd'] = date
        # start = datetime.strptime('2017-01-05','%Y-%m-%d').date()
        # while start < datetime.today().date():
        #     query['fd'] = start
        url = base_url + urlencode(query)
        # yield url
        # start += timedelta(days=7)
        rs = requests.get(url, headers=headers)
        if rs.text == '':
            continue
        js = rs.text.split('var IBhynDx={pages:1,data:')[1]
        data = eval(js[:-1])
        main_data.extend(data)
        time.sleep(2)

    temp = [i.split(',') for i in main_data]
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

    df.to_csv(
        'C:/Users/chen/Desktop/IPO_info/EastMoney/eastmoney_raw_data.csv',
        index=False,
        encoding='utf-8-sig')
    return df


def get_meetingData():
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
    df.to_csv(
        'C:/Users/chen/Desktop/IPO_info/EastMoney/eastmoney_data_meeting.csv',
        index=False,
        encoding='utf-8-sig')
    return df


def update_zzscData(newDate):
    if Path(config['eastmoney']['zzsc_pkl']).is_file:
        if newDate != config['eastmoney']['lastDate']:
            with open(config['eastmoney']['zzsc_pkl'], 'rb') as file:
                zzsc_dict = pickle.load(file)
            
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
                'fd': newDate,
                'rt': '53727636'
            }
            url = base_url + urlencode(query)
            rss = requests.get(url, headers=headers)
            if rss.text == 'var IBhynDx={pages:0,data:[{stats:false}]}':
                return 
            jss = rss.text.split('var IBhynDx={pages:1,data:')[1]
            data = eval(jss[:-1])

            for i in data:
                name = i.split(',')[1]
                if name not in zzsc_dict:
                    zzsc_dict[name] = i.split(',')[2]
                else:
                    continue
            zzsc = pd.DataFrame(zzsc_dict.items(), columns=['机构名称', '决定终止审查时间'])
            zzsc.to_csv('C:/Users/chen/Desktop/IPO_info/EastMoney/eastmoney_zzsc.csv',
                encoding='utf-8-sig',
                index=False)
            with open(config['eastmoney']['zzsc_pkl'], 'wb') as file:
                pickle.dump(zzsc_dict, file, pickle.HIGHEST_PROTOCOL)

    else:
        dateList = date_gen()
        get_zzscData(dateList)


def get_zzscData(dateList):

    zzsc_dict = {}

    for date in dateList:
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
            continue
        jss = rss.text.split('var IBhynDx={pages:1,data:')[1]
        data = eval(jss[:-1])

        for i in data:
            name = i.split(',')[1]
            if name not in zzsc_dict:
                zzsc_dict[name] = i.split(',')[2]
            else:
                continue
        time.sleep(2)

    zzsc = pd.DataFrame(zzsc_dict.items(), columns=['机构名称', '决定终止审查时间'])
    zzsc.to_csv('C:/Users/chen/Desktop/IPO_info/EastMoney/eastmoney_zzsc.csv',
                encoding='utf-8-sig',
                index=False)
    with open(config['eastmoney']['zzsc_pkl'], 'wb') as file:
        pickle.dump(zzsc_dict, file, pickle.HIGHEST_PROTOCOL)
    return zzsc


def eastmoney_cleanUP():
    east_money = pd.read_csv(
        'C:/Users/chen/Desktop/IPO_info/EastMoney/eastmoney_raw_data.csv')
    east_money.replace({'是否提交财务自查报告': ' '}, '是')
    east_money.replace({'是否提交财务自查报告': '不适用'}, '是')
    east_money['机构名称'] = east_money['机构名称'].replace(r'\*', '', regex=True)
    east_money['机构名称'] = east_money['机构名称'].replace(r'股份有限公司', '', regex=True)
    east_money['机构名称'] = east_money['机构名称'].replace(r'\(', '（', regex=True)
    east_money['机构名称'] = east_money['机构名称'].replace(r'\)', '）', regex=True)
    east_money = east_money[east_money['板块'] != '创业板']
    east_money['类型'] = pd.Categorical(east_money['类型'], 
                      categories=["已受理","已反馈","预先披露更新","","","","","已通过发审会"],
                      ordered=True)
    # east_money.sort_values(['机构名称','类型','受理日期'],ascending=[True, True,True],inplace=True)
    # east_money.to_csv('C:/Users/chen/Desktop/IPO_info/pre_cleab.csv',encoding='utf-8-sig',index=False)
    east_money.drop_duplicates(subset=['机构名称', '类型'],
                               keep='first',
                               inplace=True)
    east_money.to_csv(
        'C:/Users/chen/Desktop/IPO_info/EastMoney/eastmoney_data_cleaned.csv',
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
    shzb = {}  # 上海主板
    szzxb = {}  # 深圳中小板
    all_data = {}  # 总数据

    ekk = cleaned_easymoney_df.values.tolist()

    for i in ekk:
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

    ekk3 = zzsc_df.values.tolist()

    for i in ekk3:
        name = i[0].replace(r'股份有限公司', '')
        if name not in all_data:
            print("Error: Cannot find in zzsc", i[0])
            error_set.update({name: i[1]})
            continue
        all_data[name]['终止审查'] = i[1]

    # for key, value in all_data.items():
    #     if value['板块'] == '中小板' and value['终止审查'] == '' and value['上市日期'] == '':
    #         szzxb.update({key: value})

    #     if value['板块'] == '主板企业' and value['终止审查'] == '' and value['上市日期'] == '':
    #         shzb.update({key: value})
    return all_data, error_set

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


if __name__ == '__main__':
    # dateList = date_gen()
    # get_eastmoneyData(dateList)
    east_money_df = eastmoney_cleanUP()
    # east_money_df =  pd.read_csv('C:/Users/chen/Desktop/IPO_info/EastMoney/easymoney_data_new.csv',keep_default_na=False)
    meetingInfo_df = pd.read_csv('C:/Users/chen/Desktop/IPO_info/EastMoney/eastmoney_data_meeting.csv',keep_default_na=False)
    # meetingInfo_df = get_meetingData()
    zzsc_df = pd.read_csv('C:/Users/chen/Desktop/IPO_info/EastMoney/zzsc.csv')
    all_data,_ = gen_finalData(east_money_df,meetingInfo_df,zzsc_df) 
    print('Complete!')
    with open('C:/Users/chen/Desktop/IPO_info/zb_zxb_info.pkl','wb') as f:
        pickle.dump(all_data, f, pickle.HIGHEST_PROTOCOL)