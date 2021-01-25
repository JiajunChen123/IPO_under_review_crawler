import requests
import re
import json
import pickle
import os
import random
import time
from urllib.parse import urlencode

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',}
        #    'Accept': '*/*',
        #    'Accept-Encoding': 'gzip, deflate',
        #    'Accept-Language': 'zh-CN,zh;q=0.9',
        #    'Connection': 'keep-alive',
        #    'Host': 'listing.szse.cn'}

def index_getter(projtype):
    if projtype == 'ipo':
        biztype = 1
    elif projtype == 'refinance':
        biztype = 2
    elif projtype == 'reproperty':
        biztype = 3 
    else:
        print("Input error! Please choose the correct type of data")
        return

    params = {'bizType':biztype, 'random':random.random(),'pageIndex':0,'pageSize':1000}
    base_url = 'http://listing.szse.cn/api/ras/projectrends/query?'
    projList_url = base_url + urlencode(params)

    r = requests.get(projList_url,headers=headers)
    index_list = json.loads(r.text)
    #save_obj(index_list['data'], os.getcwd()+'\\'+'sz_index'+'_'+projtype)
    return index_list['data']


def data_getter(prjid):
    base_url = 'http://listing.szse.cn/api/ras/projectrends/details?id='
    stock_url = base_url + prjid
    r = requests.get(stock_url,headers=headers)
    stockInfo = json.loads(r.text)['data']
    base_path = os.getcwd() + stock
    directory = base_path + '\\' + stockInfo['cmpnm']
    if not os.path.exists(directory):
        os.makedirs(directory)
    save_obj(stockInfo,directory+'\\'+'sz_info')
    return stockInfo

def file_getter(stockInfo):
    base_path = os.getcwd() 
    directory = base_path + '\\' + stockInfo['cmpnm']
    if not os.path.exists(directory):
        os.makedirs(directory)
    response = stockInfo['enquiryResponseAttachment']
    disclosure = stockInfo['disclosureMaterials']
    base_url = 'http://reportdocs.static.szse.cn'
    for prj in disclosure:
        filePath = prj['dfpth']
        filename = directory + '\\'+ prj['dfnm']
        download_url = base_url + filePath
        time.sleep(random.randint(1, 3))
        r = requests.get(download_url,headers=headers)
        with open(filename,'wb') as f:
            f.write(r.content)

def save_obj(obj, directory):
    with open(directory + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(directory ):
    with open( directory + '.pkl', 'rb') as f:
        return pickle.load(f)

if __name__ == '__main__':
    proj_list = index_getter()
    # print('there are total {} stocks in the list'.format(len(proj_list)))
    # i=0
    # for proj in proj_list:
    #     i+=1
    #     print('fetching number project {},{}'.format(i,proj['cmpsnm']))
    #     prjid = proj['prjid']
    #     stockInfo = data_getter(str(prjid))
    #     # file_getter(stockInfo)
    #     time.sleep(random.randint(2,5))
    # print('Update completed!!!!')