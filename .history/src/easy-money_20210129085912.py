# 东方财富网 首发申报
from datetime import datetime,timedelta
from urllib.parse import urlencode
import pandas as pd
import requests
import re
import time
base_url = 'https://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}

query = {'type': 'NS',
         'sty' : 'NSFR',
         'st' : '1',
         'sr' : '-1',
         'p' : '1',
         'ps' : '5000',
         'js' : 'var IBhynDx={pages:(pc),data:[(x)]}',
         'mkt' : '1',
         'rt' : '53721774'
        }

def date_gen():
    r = requests.get('http://data.eastmoney.com/xg/xg/sbqy.html',headers=headers)
    r.encoding = 'gbk'
    soup = BeautifulSoup(r.text,'html.parser')

    dateList = [i.text for i in soup.findAll('option')]
    

    query = {'type': 'NS',
         'sty' : 'NSFR',
         'st' : '1',
         'sr' : '-1',
         'p' : '1',
         'ps' : '5000',
         'js' : 'var IBhynDx={pages:(pc),data:[(x)]}',
         'mkt' : '1',
         'rt' : '53721774'
        }
    start = datetime.strptime('2017-01-05','%Y-%m-%d').date()
    while start < datetime.today().date():
        query['fd'] = start
        url = base_url + urlencode(query)
        yield url
        start += timedelta(days=7)


main_data = []
for url in date_gen():
    print('Downloading date:',url)
    rs = requests.get(url,headers=headers)
    if rs.text == '':
        continue
    js = rs.text.split('var IBhynDx={pages:1,data:')[1]
    data = eval(js[:-1])
    main_data.extend(data)
    time.sleep(2)
temp = [i.split(',') for i in main_data]
columns = ['会计师事务所','保荐代表人','保荐机构','xxx','律师事务所','日期','所属行业','板块','是否提交财务自查报告',
'注册地','类型','机构名称','签字会计师','签字律师','时间戳','简称']
df = pd.DataFrame(temp,columns=columns)
df['文件链接'] = df['时间戳'].apply(lambda x: "https://notice.eastmoney.com/pdffile/web/H2_" + x + "_1.pdf")
df = df[['机构名称', '类型', '板块', '注册地', '保荐机构','保荐代表人', '律师事务所', '签字律师','会计师事务所', 
'签字会计师', '是否提交财务自查报告', '所属行业','日期','xxx', '时间戳', '保荐机构','文件链接']]
# df = df[df['板块'] != '创业板']
df.to_csv('C:/Users/chen/Desktop/IPO_info/eastmoney_pre_data.csv',index=False,encoding='utf-8-sig')



# for i in ['2','4']:
#     query = {'type': 'NS',
#             'sty' : 'NSSH',
#             'st' : '1',
#             'sr' : '-1',
#             'p' : '1',
#             'ps' : '5000',
#             'js' : 'var IBhynDx={pages:(pc),data:[(x)]}',
#             'mkt' : i,
#             'rt' : '53723990'
#             }

#     url = base_url + urlencode(query)
#     rss = requests.get(url,headers=headers)
#     jss = rss.text.split('var KIBhynDx={pages:1,data:')[1]
#     data = eval(jss[:-1])

#     temp = [j.split(',') for j in data]

#     columns = ['时间戳','yyy','公司代码','机构名称','详情链接','申报日期','上会日期','申购日期','上市日期','9','拟发行数量','发行前总股本','发行后总股本','13','占发行后总股本比例','当前状态','上市地点','主承销商','承销方式','发审委委员','网站','简称']
#     df = pd.DataFrame(temp,columns=columns)
#     df['文件链接'] = df['时间戳'].apply(lambda x: "https://notice.eastmoney.com/pdffile/web/H2_" + x + "_1.pdf")
#     df['详情链接'] = df['公司代码'].apply(lambda x: "data.eastmoney.com/xg/gh/detail/" + x + ".html")
#     df = df[['机构名称', '当前状态', '上市地点', '拟发行数量', '申报日期','上会日期', '申购日期', '上市日期', '主承销商','承销方式', '9', '发行前总股本','发行后总股本','13','占发行后总股本比例','发审委委员','网站','公司代码','yyy','时间戳', '简称', '详情链接','文件链接']]
#     df.to_csv('C:/Users/chen/Desktop/IPO_info/easymoney_data_{}_onmeeting.csv'.format(i),index=False,encoding='utf-8-sig')



from urllib.parse import urlencode
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
base_url = 'https://datainterface.eastmoney.com/EM_DataCenter/JS.aspx?'

v
zzsc_dict = {}

for date in dateList:
    query = {'type': 'NS',
            'sty' : 'NSSE',
            'st' : '1',
            'sr' : '-1',
            'p' : '1',
            'ps' : '500',
            'js' : 'var IBhynDx={pages:(pc),data:[(x)]}',
            'mkt' : '4',
            'stat':'zzsc',
            'fd' : date,
            'rt' : '53727636'
            }

    url = base_url + urlencode(query)
    rss = requests.get(url,headers=headers)
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

zzsc = pd.DataFrame(zzsc_dict.items(),columns = ['机构名称','决定终止审查时间'])
zzsc.to_csv('C:/Users/chen/Desktop/IPO_info/zzsc.csv',encoding='utf-8-sig',index=False)
