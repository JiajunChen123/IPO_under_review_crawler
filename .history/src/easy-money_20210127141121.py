# 东方财富网 首发申报
from datetime import datetime
from urllib.parse import urlencode
import pandas as pd
import requests
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
    start = datetime.strptime('2017-01-05').date()
    while start < datetime.today().date():
        query['fd'] = start
        url = base_url + urlencode(query)
        yield url

main_data = []
for url in date_gen():
    rs = requests.get(url,headers=headers)
    if rs.text == '':
        continue
    js = rs.text.split('var KIBhynDx={pages:1,data:')[1]
    data = eval(js[:-1])
    main_data.extend(data)

temp = [i.strip(',') for i in main_data]
columns = ['会计师事务所','保荐代表人','保荐机构','xxx','律师事务所','日期','所属行业','板块','是否提交财务自查报告',
'注册地','类型','机构名称','签字会计师','签字律师','时间戳','简称']
df = pd.DataFrame(temp,columns=columns)
df['文件链接'] = df['时间戳'].apply(lambda x: "https://notice.eastmoney.com/pdffile/web/H2_" + x + "_1.pdf")
df = df[['机构名称', '类型', '板块', '注册地', '保荐机构','保荐代表人', '律师事务所', '签字律师','会计师事务所', 
'签字会计师', '是否提交财务自查报告', '所属行业','日期','xxx', '时间戳', '保荐机构','文件链接']]
df.to_csv('C:/Users/chen/Desktop/IPO_info/easymoney_data.csv',index=False,encoding='utf-8-sig')



query = {'type': 'NS',
         'sty' : 'NSSH',
         'st' : '1',
         'sr' : '-1',
         'p' : '1',
         'ps' : '5000',
         'js' : 'var IBhynDx={pages:(pc),data:[(x)]}',
         'mkt' : '2',
         'rt' : '53723990'
        }

url = base_url + urlencode(query)
rss = requests.get(url,headers=headers)
jss = rss.text.split('var KIBhynDx={pages:1,data:')[1]
data = eval(jss[:-1])



columns = ['时间戳','yyy','公司代码','机构名称','详情链接','申报日期','上会日期','申购日期','上市日期','9','拟发行数量','发行前总股本','发行后总股本','13','占发行后总股本比例','当前状态','上市地点','主承销商','承销方式','发审委委员','网站','简称']
df = pd.DataFrame(temp,columns=columns)
df['文件链接'] = df['时间戳'].apply(lambda x: "https://notice.eastmoney.com/pdffile/web/H2_" + x + "_1.pdf")
df['详情链接'] = df['公司代码'].apply(lambda x: "data.eastmoney.com/xg/gh/detail/" + x + ".html")
df = df[['机构名称', '当前状态', '上市地点', '拟发行数量', '申报日期','上会日期', '申购日期', '上市日期', '主承销商','承销方式', '9', '发行前总股本','发行后总股本','13','占发行后总股本比例','发审委委员','网站','公司代码','yyy','时间戳', '简称', '详情链接','文件链接']]
# df.to_csv('C:/Users/chen/Desktop/IPO_info/easymoney_data.csv',index=False,encoding='utf-8-sig')
df.head()