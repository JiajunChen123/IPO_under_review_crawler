import requests
import re
import json
import pickle
import os
import random
import time
import configparser
from urllib.parse import urlencode
from utils import save_pickle,load_pickle
from datetime import datetime
from preprocessing import data_process
from html_gen import gen_html
# 上海证券交易所-科创板股票审核网

config = configparser.ConfigParser()

config.read('Config.ini')

IPO_sqlId = config['kcb']['IPO_sqlId']
refinance_sqlId = config['kcb']['refinance_sqlId']
reproperty_sqlId = config['kcb']['reproperty_sqlId']

base_url = config['kcb']['base_url']
headers = config['kcb']['headers']

def url_parser(stockAidotNum, sqltype, projtype):
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
    try:
        return re.search('^[^(]*?\((.*)\)[^)]*$', jsonp_str).group(1)
    except:
        raise ValueError('Invalid JSONP')



def data_getter(stockAidotNum, projtype):
    base_path = os.getcwd() + '/data/IPO/科创板/'

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
    directory = base_path + '/' + stock_allInfo['info'][0]['stockAuditName']
    if not os.path.exists(directory):
        os.makedirs(directory)
    save_pickle(stock_allInfo, directory + '/' + 'info.pkl')
    return stock_allInfo



def file_getter(stockInfo):

    base_path = os.getcwd() + '/data/IPO/科创板/'
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
    save_pickle(stockInfo, directory + '\\' + 'info')


def index_getter(projtype):
    if projtype == 'ipo':
        index_url = 'https://query.sse.com.cn/statusAction.do?jsonCallBack=jsonpCallback47570&isPagination=true&sqlId=SH_XM_LB&pageHelp.pageSize=1000&offerType=&commitiResult=&registeResult=&csrcCode=&currStatus=&order=updateDate%7Cdesc&keyword=&auditApplyDateBegin=&auditApplyDateEnd=&_=1611139628341'
    elif projtype == 'refinance':
        index_url = 'https://query.sse.com.cn/bgczStatusAction.do?jsonCallBack=jsonpCallback52431&isPagination=true&sqlId=GP_BGCZ_XMLB&pageHelp.pageSize=1000&offerType=&commitiResult=&registeResult=&csrcCode=&currStatus=&order=updateDate%7Cdesc&keyword=&auditApplyDateBegin=&auditApplyDateEnd=&_=1611139628341'
    elif projtype == 'reproperty':
        index_url = 'https://query.sse.com.cn/zrzStatusAction.do?jsonCallBack=jsonpCallback89527&isPagination=true&sqlId=GP_ZRZ_XMLB&pageHelp.pageSize=1000&offerType=&commitiResult=&registeResult=&csrcCode=&currStatus=&order=updateDate%7Cdesc&keyword=&auditApplyDateBegin=&auditApplyDateEnd=&_=1611139628341'
    

    r = requests.get(index_url, headers=headers)

    js = jsonp_parser(r.text)
    index_list = json.loads(js)['result']

    save_pickle(index_list, os.getcwd() + '/saved_config/' + 'shkcb_index.pkl')
    return index_list



def shkcb_check_update():
    prjtype = 'ipo'
    try: 
        proj_list_old = load_pickle(os.getcwd()+'/saved_config/shkcb_index.pkl')
        proj_list_new = index_getter(prjtype)
        stocksInfo = load_pickle(os.getcwd()+'/saved_config/shkcb_stocksInfo.pkl')
        updated_idx = [index for (index, d) in enumerate(proj_list_new) if datetime.strptime(d['updateDate'],'%Y%m%d%H%M%S').date() == datetime.today().date()]
        if updated_idx == []:
            print("Nothing has changed!")
            return
        else:
            print("there are {} projects have been updated!".format(len(updated_idx)))
            for idx in updated_idx:
                raw_data = data_getter(proj_list_new[idx]['stockAuditNum'])
                cleaned_data = data_process(raw_data)
                print('company:', cleaned_data['baseInfo']['cmpName'],'is updated')
                html = gen_html(cleaned_data)
                new_idx = next((index for (index, d) in enumerate(stocksInfo) if d["baseInfo"]['cmpName'] == proj_list_new[idx]['cmpName']), None)
                stocksInfo[idx] = cleaned_data

            save_pickle(stocksInfo, os.getcwd()+'/saved_config/szcyb_stocksInfo.pkl')
            print("all stocksInfo are updated!")   
            return
    except FileNotFoundError:
        proj_list = index_getter()
        print('there are total {} stocks in the list'.format(len(proj_list)))
        i = 0
        # proj_list = load_pickle('C:/Users/chen/Desktop/IPO_info/shkcb_index.pkl')
        for proj in proj_list:
            i += 1
            print('fetching number project {},{}'.format(i,
                                                        proj['stockAuditName']))
            stockAuditNum = proj['stockAuditNum']
            raw_data = data_getter(stockAuditNum)
            cleaned_data = data_process(raw_data)
            print('company:', cleaned_data['baseInfo']['cmpName'],'is updated')
            html = gen_html(cleaned_data)
            # file_getter(stockInfo)
            time.sleep(random.randint(1, 4))
        get_allStockInfo()
    else:
        print('Update completed!!!!')
        return

def get_allStockInfo():
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()+'/data/IPO/科创板'):
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
    saved_path = os.getcwd()+'/saved_config/shkcb_stocksInfo.pkl'
    save_pickle(stocksInfo, saved_path)
    return 


if __name__ == '__main__':
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
