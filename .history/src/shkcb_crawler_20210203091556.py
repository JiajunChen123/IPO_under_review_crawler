#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   shkcb_crawler.py
@Time    :   2021/02/03 09:11:57
@Author  :   Jiajun Chen 
@Version :   1.0
@Contact :   554001000@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
'''

import requests
import re
import json
import pickle
import os
import random
import time
import configparser
from urllib.parse import urlencode
from utils import save_pickle, load_pickle
from datetime import datetime
from preprocessing import data_process
from html_gen import gen_html

# 上海证券交易所-科创板股票审核网

# Parameters
IPO_sqlId = {
    'info': 'SH_XM_LB',
    'release': 'GP_GPZCZ_SHXXPL',
    'status': 'GP_GPZCZ_XMDTZTTLB',
    'result': 'GP_GPZCZ_SSWHYGGJG',
    'res': 'GP_GPZCZ_XMDTZTYYLB'
}
refinance_sqlId = {
    'info': 'GP_BGCZ_XMLB',
    'release': 'GP_BGCZ_SSWHYGGJG',
    'status': 'GP_BGCZ_XMDTZTTLB'
}
reproperty_sqlId = {
    'status': 'GP_ZRZ_XMDTZTTLB',
    'release': 'GP_ZRZ_GGJG',
    'result': '',
    'res': 'GP_ZRZ_XMZTYYLB',
    'info': 'GP_ZRZ_XMLB'
}
headers = {
    'header':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'referer': 'https://kcb.sse.com.cn/',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'JSESSIONID=A53F3AFE1C4FC9029CDF0AB8305EC4D0',
    'Host': 'query.sse.com.cn'
}



base_url = 'https://query.sse.com.cn/'


def url_parser(stockAidotNum, sqltype, projtype='ipo'):
    if projtype == 'ipo':
        sqlId = IPO_sqlId[sqltype]
    elif projtype == 'refinance':
        sqlId = refinance_sqlId[sqltype]

    elif projtype == 'reproperty':
        sqlId = reproperty_sqlId[sqltype]
    if sqlId == '':
        return ''
    else:
        url = base_url + 'commonSoaQuery.do?' + 'jsonCallBack=jsonpCallback28511843' '&sqlId=' + sqlId + '&stockAuditNum=' + stockAidotNum
        return url


def jsonp_parser(jsonp_str):
    # 解析返回的js文件
    try:
        return re.search('^[^(]*?\((.*)\)[^)]*$', jsonp_str).group(1)
    except:
        raise ValueError('Invalid JSONP')


def data_getter(stockAidotNum, projtype='ipo'):
    base_path = './data/IPO/科创板/'

    stock_allInfo = {}
    for sqltype in ['info', 'status', 'release', 'result', 'res']:

        url = url_parser(stockAidotNum, sqltype, projtype)
        if url != '':
            rs = requests.get(url, headers=headers)
            raw_data = jsonp_parser(rs.text)
            data = json.loads(raw_data)['pageHelp']['data']
            stock_allInfo[sqltype] = data
        else:
            stock_allInfo[sqltype] = ''
    directory = base_path + '/' + stock_allInfo['info'][0]['stockIssuer'][0][
        's_issueCompanyFullName']
    if not os.path.exists(directory):
        os.makedirs(directory)
    save_pickle(stock_allInfo, directory + '/' + 'shkcb_info.pkl')
    return stock_allInfo


def file_getter(stockInfo):
    # 将项目所有文件下载到同名文件夹中
    base_path ='./data/IPO/科创板/'
    directory = base_path + stockInfo['info'][0]['stockAuditName']
    if not os.path.exists(directory):
        os.makedirs(directory)
    base_url = 'http://static.sse.com.cn/stock'

    for i in stockInfo['release']:
        filePath = i['filePath']
        filename = directory + '\\' + i['fileTitle'] + '.pdf'
        url = base_url + filePath
        time.sleep(random.randint(1, 5))
        r = requests.get(url, headers=headers)
        with open(filename, 'wb') as f:
            f.write(r.content)


def index_getter(projtype):
    # 获取最新项目列表
    if projtype == 'ipo':
        index_url = 'https://query.sse.com.cn/statusAction.do?jsonCallBack=jsonpCallback47570&isPagination=true&sqlId=SH_XM_LB&pageHelp.pageSize=1000&offerType=&commitiResult=&registeResult=&csrcCode=&currStatus=&order=updateDate%7Cdesc&keyword=&auditApplyDateBegin=&auditApplyDateEnd=&_=1611139628341'
    elif projtype == 'refinance':
        index_url = 'https://query.sse.com.cn/bgczStatusAction.do?jsonCallBack=jsonpCallback52431&isPagination=true&sqlId=GP_BGCZ_XMLB&pageHelp.pageSize=1000&offerType=&commitiResult=&registeResult=&csrcCode=&currStatus=&order=updateDate%7Cdesc&keyword=&auditApplyDateBegin=&auditApplyDateEnd=&_=1611139628341'
    elif projtype == 'reproperty':
        index_url = 'https://query.sse.com.cn/zrzStatusAction.do?jsonCallBack=jsonpCallback89527&isPagination=true&sqlId=GP_ZRZ_XMLB&pageHelp.pageSize=1000&offerType=&commitiResult=&registeResult=&csrcCode=&currStatus=&order=updateDate%7Cdesc&keyword=&auditApplyDateBegin=&auditApplyDateEnd=&_=1611139628341'

    r = requests.get(index_url, headers=headers)

    js = jsonp_parser(r.text)
    index_list = json.loads(js)['result']

    save_pickle(index_list,'./saved_config/' + 'shkcb_index.pkl')
    return index_list


def shkcb_check_update():
    # 主函数，先判断有无更新，有新增项目则增量更新
    prjtype = 'ipo'
    try:
        proj_list_new = index_getter(prjtype)
        stocksInfo = load_pickle('./saved_config/shkcb_stocksInfo.pkl')
        updated_idx = [
            index for (index, d) in enumerate(proj_list_new)
            if datetime.strptime(d['updateDate'], '%Y%m%d%H%M%S').date() ==
            datetime.today().date()
        ]
        if updated_idx == []:
            print("Nothing has changed!")
            return
        else:
            print("there are {} projects have been updated!".format(
                len(updated_idx)))
            for idx in updated_idx:
                raw_data = data_getter(proj_list_new[idx]['stockAuditNum'])
                cleaned_data = data_process(raw_data)
                print('company:', cleaned_data['baseInfo']['cmpName'],
                      'is updated')
                html = gen_html(cleaned_data)
                new_idx = next(
                    (index
                     for (index, d) in enumerate(stocksInfo) if d["baseInfo"]
                     ['cmpName'] == proj_list_new[idx]['cmpName']), None)
                stocksInfo[idx] = cleaned_data

            save_pickle(stocksInfo,'./saved_config/szcyb_stocksInfo.pkl')
            print("all stocksInfo are updated!")
            return
    except FileNotFoundError:
        # 若找不到本地目录文件，则重新
        proj_list = index_getter(prjtype)
        # proj_list = load_pickle('./saved_config/shkcb_index.pkl')
        # print('there are total {} stocks in the list'.format(len(proj_list)))
        i = 0
        for proj in proj_list:
            i += 1
            print('fetching number project {},{}'.format(
                i, proj['stockAuditName']))
            stockAuditNum = proj['stockAuditNum']
            raw_data = data_getter(stockAuditNum)
            cleaned_data = data_process(raw_data)
            print('company:', cleaned_data['baseInfo']['cmpName'],
                  'is updated')
            html = gen_html(cleaned_data)
            # file_getter(stockInfo)
            time.sleep(random.randint(1, 4))
        get_allStockInfo()
    else:
        print('Update completed!!!!')
        return


def get_allStockInfo():
    listOfFiles = list()
    for (dirpath, dirnames,
         filenames) in os.walk('./data/IPO/科创板'):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    stocksInfo = []
    for i in listOfFiles:
        if os.path.basename(i) == 'clean_info.pkl':
            # print('clean up company:', os.path.dirname(i))
            # raw_data = load_pickle(i)
            # cleaned_data = data_process(raw_data)
            clean_data = load_pickle(i)
            stocksInfo.append(clean_data)
    # to_dataframe(allStock_info)
    saved_path ='./saved_config/shkcb_stocksInfo.pkl'
    save_pickle(stocksInfo, saved_path)
    return


if __name__ == '__main__':
    shkcb_check_update()
    # raw_data = data_getter('844')
    # print(raw_data['info'][0]['stockAuditName'])
    # cleaned_data = data_process(raw_data)
    # print(cleaned_data['baseInfo']['cmpName'])
    # #proj_list = index_getter()
    # # print('there are total {} stocks in the list'.format(len(proj_list)))
    # i = 0
    # proj_list = load_pickle('C:/Users/chen/Desktop/IPO_info/shkcb_index.pkl')
    # for proj in proj_list[405:]:
    #     i += 1
    #     print('fetching number project {},{}'.format(i,
    #                                                  proj['stockAuditName']))
    #     stockAuditNum = proj['stockAuditNum']
    #     stockInfo = data_getter(stockAuditNum)
    #     # file_getter(stockInfo)
    #     time.sleep(random.randint(1, 4))
