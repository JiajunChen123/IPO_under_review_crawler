#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   szcyb_crawler.py
@Time    :   2021/02/04 13:51:38
@Author  :   Jiajun Chen 
@Version :   1.0
@Contact :   554001000@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
'''

# 深圳证券交易所创业板审核项目爬虫


import requests
import re
import json
import pickle
import os
import random
import datetime
import time
from urllib.parse import urlencode
from utils import save_pickle, load_pickle
from preprocessing import data_process
from html_gen import gen_html


headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
}

def index_getter(projtype='ipo'):
    '''
    获取目录页
    '''
    if projtype == 'ipo':
        biztype = 1
    elif projtype == 'refinance':
        biztype = 2
    elif projtype == 'reproperty':
        biztype = 3
    else:
        print("Input error! Please choose the correct type of data")
        return

    params = {
        'bizType': biztype,
        'random': random.random(),
        'pageIndex': 0,
        'pageSize': 1000
    }
    base_url = 'http://listing.szse.cn/api/ras/projectrends/query?'
    projList_url = base_url + urlencode(params)

    r = requests.get(projList_url, headers=headers)
    index_list = json.loads(r.text)
    save_pickle(index_list['data'],
                './saved_config/'+ 'szcyb_index.pkl')
    return index_list['data']


def data_getter(prjid):
    '''
    获取单个项目详细信息
    '''

    base_url = 'http://listing.szse.cn/api/ras/projectrends/details?id='
    stock_url = base_url + str(prjid)
    r = requests.get(stock_url, headers=headers)
    stockInfo = json.loads(r.text)['data']
    base_path = './data/IPO/创业板/'

    directory = base_path + '/' + stockInfo['cmpnm']
    if not os.path.exists(directory):
        os.makedirs(directory)
    save_pickle(stockInfo, directory + '/' + 'szcyb_info.pkl')
    return stockInfo


def file_getter(stockInfo):
    '''
    获取各个项目所有文件，保存在同名文件夹中
    '''
    base_path = './data/IPO/创业板/'
    directory = base_path + stockInfo['cmpnm']
    if not os.path.exists(directory):
        os.makedirs(directory)
    response = stockInfo['enquiryResponseAttachment']
    disclosure = stockInfo['disclosureMaterials']
    base_url = 'http://reportdocs.static.szse.cn'
    for prj in disclosure:
        filePath = prj['dfpth']
        filename = directory + '/' + prj['dfnm']
        download_url = base_url + filePath
        time.sleep(random.randint(1, 3))
        r = requests.get(download_url, headers=headers)
        with open(filename, 'wb') as f:
            f.write(r.content)




def get_allStockInfo():
    '''
    汇集所有项目信息
    '''
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk('./data/IPO/创业板'):
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
    saved_path = './saved_config/szcyb_stocksInfo.pkl'
    save_pickle(stocksInfo, saved_path)
    return




if __name__ == '__main__':
    szcyb_check_update()
