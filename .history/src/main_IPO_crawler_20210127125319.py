
import requests
from bs4 import BeautifulSoup
import time
import re
import json



headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}

def date_gen(start=2014):
    now = int(time.ctime().strip()[-1])
    for i in range(start,now+1):
        yield  {'startDate': '{}-01-01'.format(i),
            'endDate': '{}-12-31'.format(i)}

sz_data_list = []
sh_data_list = []
def find_data(soup,container):
    k =soup.find(attrs={'class':'m-table2 m-table2-0'}).findAll('tr')[1:]
    for idx, tr in enumerate(k):
        if idx != 0:
            tds = tr.find_all('td')
            container.append({
                '公司名称': tds[0].contents[0].strip(),
                '披露类型': tds[1].contents[0].strip(),
                '所属板块': tds[2].contents[0].strip(),
                '保荐机构': tds[3].get_text().strip(),
                '更新时间': tds[4].contents[0].strip(),
                '公告': tds[5].get_text().strip(),
                'link': re.search(r'(?<=downloadPdf1\().+\.pdf',k[0]['onclick']).group()
            })

def Process(post_data,base_url,container):
    first_page = base_url + 'index_f.html'
    r = requests.post(first_page,data=post_data,headers=headers)
    soup = BeautifulSoup(r.text,'html5lib')
    find_data(soup,container)
    numPages = int(soup.find(attrs={'class':'g-ul'}).findAll('li')[-1].find('b').contents[0])
    current_page = 1
    while current_page < numPages:
        current_page +=1 
        print('Dealing on page:',current_page)
        next_url = base_url + 'index_{}_f.html'.format(current_page)
        r = requests.post(next_url,data=post_data, headers=headers)
        soup = BeautifulSoup(r.text,'html5lib')
        find_data(soup,container)
        time.sleep(2)
    print('Data collect completed!')



if __name__ == '__main__':
    sz_data_list = []
    sh_data_list = []
    sz_base_url = 'http://eid.csrc.gov.cn/ipo/101011/'
    sh_base_url = 'http://eid.csrc.gov.cn/ipo/101010/'

    date = date_gen()
    for i in date:
        Process(i,sz_base_url,sz_data_list)
        Process(i,sh_base_url,    with open(directory + '.pkl', 'wb') as f:
    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)sh_data_list)

