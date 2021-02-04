#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   csrc_reply.py
@Time    :   2021/02/04 14:14:51
@Author  :   Jiajun Chen 
@Version :   1.0
@Contact :   554001000@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
'''

# 证监会发行监管部首次公开发行反馈意见爬虫 


from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import requests
import time
from datetime import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}

baseUrl = 'http://www.csrc.gov.cn/pub/newsite/fxjgb/scgkfxfkyj/'

def download_page(nexturl):
    r = requests.get(nexturl,headers= headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text,'html.parser')
    projList = soup.find(id='myul').findAll('a')
    for proj in projList:
        href= proj['href']
        docUrl = baseUrl + href
        title = proj.text
        print('fetching: ',title)

        download_doc(docUrl,title)
        time.sleep(2)


def download_doc(docUrl,title):
    pageInfo = requests.get(docUrl,headers=headers)
    pageInfo.encoding='utf-8'
    docLink = re.findall(r'file_appendix=\'<a href=\"(.*)\">',pageInfo.text)[0]
    doc = requests.get(urljoin(docUrl,docLink),headers=headers,stream=True)
    with open('C:/Users/chen/Desktop/IPO_info/data/证监会文件/{}.docx'.format(title),'wb') as f:
            f.write(doc.content)


def get_all_file():

    r = requests.get(baseUrl,headers= headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text,'html.parser')
    numPage = re.findall(r'var countPage = (.*)//',soup.text)[0]
    numPage = int(numPage)
    download_page(baseUrl)

    for i in range(1,numPage):
        nextUrl = baseUrl + 'index_{}.html'.format(i)
        download_page(nextUrl)

def check_update():
    today = datetime.today().date().strftime('%Y-%m-%d')
    
    baseUrl = 'http://www.csrc.gov.cn/pub/newsite/fxjgb/scgkfxfkyj/'
    r = requests.get(baseUrl,headers=headers)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text,'html.parser')

    
    for i in soup.find(id='myul').findAll('li'):
        if i.span.get_text() == today:
            docUrl = baseUrl + i.a['href']
            title = i.a.text
            print("")
            download_doc(docUrl,title)