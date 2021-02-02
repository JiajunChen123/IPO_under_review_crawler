import requests
from bs4 import BeautifulSoup
import time

# login = {'user':'13710149700',
        #  'password':'123456'}

# 使用的网站是企查查
# requests.post('https://www.qichamao.com',data=login,headers=afterLogin_headers)

afterLogin_headers = {'Cookie':'qznewsite.uid=y4eseo3a1q4xbrwimor3o5tm; Hm_lvt_55ad112b0079dd9ab00429af7113d5e3=1611805092; qz.newsite=6C61702DD95709F9EE190BD7CCB7B62C97136BAC307B6F0B818EC0A943307DAB61627F0AC6CD818268C10D121B37F840C1EF255513480EC3012A7707443FE523DD7FF79A7F3058E5E7FB5CF3FE3544235D5313C4816B54C0CDB254F24D8ED5235B722BCBB23BE62B19A2370E7F0951CD92A731FE66C208D1BE78AA64758629806772055F7210C67D442DE7ABBE138EF387E6258291F8FBF85DFF6C785E362E2903705A0963369284E8652A61531293304D67EBB8D28775FBC7D7EBF16AC3CCA96F5A5D17; Hm_lpvt_55ad112b0079dd9ab00429af7113d5e3=1611892605',
    'Referer':'https://www.qichamao.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}

def get_compInfo(comp):
    r = requests.get('https://www.qichamao.com/search/all/{}'.format(comp),headers=afterLogin_headers)
    r.raise_for_status()
    r.encoding = 'utf-8' #linux utf-8
    soup = BeautifulSoup(r.text,features="html.parser")
    url = 'http://www.qichamao.com' + soup.find(attrs={'class':'listsec_con'}).a['href']
    # soup.find(attrs={'class':'listsec_con'})
    time.sleep(5)
    rs = requests.get(url,headers=afterLogin_headers)
    rs.encoding='utf-8'
    soup2 = BeautifulSoup(rs.text,'html.parser')
    info = soup2.find(attrs={'class':'qd-table-body li-half f14'}).findAll('div')
    info = [i.get_text().strip() for i in info]
    compinfo = {'法定代表人':info[0],
                '纳税人识别号':info[1], 
                '名称':info[2],
                '机构代码':info[3],
                '注册号':info[4],
                '注册资本':info[5],
                '统一社会信用代码':info[6],
                '登记机关':info[7],
                '经营状态':info[8],
                '成立日期':info[9],
                '企业类型':info[10],
                '经营期限':info[11],
                '所属地区':info[12],
                '核准时间':info[13],
                '企业地址':info[14],
                '经营范围':info[15]}
    return compinfo


if __name__ == '__main__':
    compList = 
    for i in compList:
        compinfo = get_compInfo(i)
    import csv
    csv_columns = ['法定代表人','纳税人识别号','名称','机构代码','注册号','注册资本','','','','','','']
dict_data = [
{'No': 1, 'Name': 'Alex', 'Country': 'India'},
{'No': 2, 'Name': 'Ben', 'Country': 'USA'},
{'No': 3, 'Name': 'Shri Ram', 'Country': 'India'},
{'No': 4, 'Name': 'Smith', 'Country': 'USA'},
{'No': 5, 'Name': 'Yuva Raj', 'Country': 'India'},
]
csv_file = "credit.csv"
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
except IOError:
    print("I/O error")