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

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import requests
import time
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

        pageInfo = requests.get(docUrl,headers=headers)
        pageInfo.encoding='utf-8'
        docLink = re.findall(r'file_appendix=\'<a href=\"(.*)\">',pageInfo.text)[0]
        doc = requests.get(urljoin(docUrl,docLink),headers=headers,stream=True)
        with open('C:/Users/chen/Desktop/IPO_info/data/证监会文件/{}.docx'.format(title),'wb') as f:
                f.write(doc.content)
        time.sleep(2)



r = requests.get(baseUrl,headers= headers)
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text,'html.parser')
numPage = re.findall(r'var countPage = (.*)//',soup.text)[0]
numPage = int(numPage)
download_page(baseUrl)

for i in range(1,numPage):
    nextUrl = baseUrl + 'index_{}.html'.format(i)
    download_page(nextUrl)