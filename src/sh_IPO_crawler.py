import requests
import re
import json
import pickle
import os
import random
import time

# 上海证券交易所-科创板股票审核网

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
    'Cookie': 'JSESSIONID=C2EE2264D8056DC8BF3AB0DC23D26171',
    'Host': 'query.sse.com.cn'
}

base_url = 'https://query.sse.com.cn/'


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


def save_obj(obj, directory):
    with open(directory + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(directory):
    with open(directory + '.pkl', 'rb') as f:
        return pickle.load(f)



def data_getter(stockAidotNum, projtype):
    base_path = os.getcwd()

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
    directory = base_path + '\\' + stock_allInfo['info'][0]['stockAuditName']
    if not os.path.exists(directory):
        os.makedirs(directory)
    save_obj(stock_allInfo, directory + '\\' + 'info')
    return stock_allInfo



def file_getter(stockInfo):

    base_path = os.getcwd()
    directory = base_path + '\\' + stockInfo['info'][0]['stockAuditName']
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
    save_obj(stockInfo, directory + '\\' + 'info')


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

    save_obj(index_list, os.getcwd() + '\\' + 'sh_index'+'_'+projtype)
    return index_list


if __name__ == '__main__':
    #proj_list = index_getter()
    # print('there are total {} stocks in the list'.format(len(proj_list)))
    i = 0
    proj_list = load_obj('C:/Users/chen/Desktop/IPO_info/sh_index')
    for proj in proj_list[405:]:
        i += 1
        print('fetching number project {},{}'.format(i,
                                                     proj['stockAuditName']))
        stockAuditNum = proj['stockAuditNum']
        stockInfo = data_getter(stockAuditNum)
        # file_getter(stockInfo)
        time.sleep(random.randint(1, 4))
