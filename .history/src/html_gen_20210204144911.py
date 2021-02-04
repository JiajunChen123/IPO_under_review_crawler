#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   html_gen.py
@Time    :   2021/02/04 14:49:02
@Author  :   Jiajun Chen 
@Version :   1.0
@Contact :   554001000@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
'''

# 辅助

import pickle 
from bs4 import BeautifulSoup
import datetime
import json
import os
from utils import load_pickle
# template import

def load_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(),'html.parser')
    return soup


def generate_info(data,soup):
    '''
    # 文件格式
    info[0] : data.cmpnm  公司全称
    info[1] : data.cmpsnm 公司简称
    info[2] : data.acptdt 受理日期
    info[3] : data.updtdt 更新日期
    info[4] : data.prjst  审核状态
    info[5] : data.issueAmount 预计融资金额
    info[6] : data.sprinst 保荐机构
    info[7] ：data.sprrep  保荐代表人
    info[8] : data.acctFirm 会计师事务所
    info[9] : data.acctsgnt 签字会计师
    info[10] : data.lawfm  律师事务所
    info[11] : data.lglsgnt 签字律师
    info[12] : data.evalinst 评估机构
    info[13] : data.evalsgnt 签字评估师
    info[14] : data.lastestAuditEndDate 最近一期审计基准日
'''


    info = soup.findAll(attrs={'class':'info'})
    new_info = [data['baseInfo']['cmpName'],data['baseInfo']['cmpAbbrname'],data['baseInfo']['acptDate'],data['baseInfo']['updtDate'],data['baseInfo']['currStatus'],str(data['baseInfo']['issueAmount']),data['baseInfo']['sprInst'],data['baseInfo']['sprRep'],data['baseInfo']['acctFirm'],data['baseInfo']['acctSgnt'],data['baseInfo']['lawFirm'],data['baseInfo']['lglSgnt'],data['baseInfo']['evalInst'],data['baseInfo']['evalSgnt']]
    for (tag,new_string) in zip(info,new_info):
        tag.string.replace_with(new_string)

def generate_title(data,soup):
    title = soup.find(attrs={'class':'project-title'})
    # 补充深/沪标签
    title.string.replace_with(data['baseInfo']['cmpName'])


def generate_release(data,soup):
    ftype = ['招股说明书','发行保荐书','上市保荐书','审计报告','法律意见书']
    for j in range(1,6):
        for i in range(3):
            tempsoup = soup.findAll(attrs={'class':'info-disc-table'})[0].findAll('tr')[j].findAll(attrs={'class':'text-center'})[i]
            d = [(material['fdate'],material['fphynm']) for material in data['disclosureMaterial'] \
if material['ftype'] == ftype[j-1] if material['fstatus']== i+1]
            if len(d) == 0:
                tempsoup.string = "--" 
            else:
                d = sorted(d, key=lambda x: datetime.datetime.strptime(x[0], '%Y-%m-%d'), reverse=False)
                for time,link in d:
                    new_tag = soup.new_tag("a", href='./'+data['baseInfo']['cmpName'] +'/'+link, style="display:block;")
                    new_tag.string = time
                    tempsoup.append(new_tag)

def generate_response(data,soup):
    tempsoup = soup.findAll(attrs={'class':'info-disc-table'})[1].findAll('tbody')[0]
    length = len(data['responseAttachment'])
    if length ==0:
        new_soup = BeautifulSoup('<tr style="border:none;"><td colspan="10"><div class="report-nodata">\
<span class="nodata-text">暂无数据！</span></div></td></tr>','html.parser')
        tempsoup.append(new_soup)
    else:
        for i in range(length):
            new_soup = BeautifulSoup('<tr><td></td><td><a target="_blank"></td><td class="text_center">\
</td></tr>', 'html.parser')
            new_soup.a.string = data['responseAttachment'][i]['fname']
            new_soup.a['href'] = './'+data['baseInfo']['cmpName']+ '/'+ \
data['responseAttachment'][i]['fname']
            new_soup.td.string = str(i+1)
            new_soup.find(attrs={'class':'text_center'}).string = data['responseAttachment'][i]['fdate']
            tempsoup.append(new_soup)

def generate_meeting(data,soup):
    tempsoup = soup.findAll(attrs={'class':'info-disc-table'})[2].findAll('tbody')[0]
    length = len(data['meetingAttachment'])
    if length == 0:
        new_soup = BeautifulSoup('<tr style="border:none;"><td colspan="10"><div class="report-nodata">\
<span class="nodata-text">暂无数据！</span></div></td></tr>','html.parser')
        tempsoup.append(new_soup)
    else:
        for i in range(length):
            new_soup = BeautifulSoup('<tr><td></td><td><a target="_blank"></td><td class="text_center">\
</td></tr>', 'html.parser')
            new_soup.a.string = data['meetingAttachment'][i]['ftitle']
            new_soup.a['href'] = './'+data['baseInfo']['cmpName']+ '/'+ \
data['meetingAttachment'][i]['fname']
            new_soup.td.string = str(i+1)
            new_soup.find(attrs={'class':'text_center'}).string = data['meetingAttachment'][i]['fdate']
            tempsoup.append(new_soup)

def generate_registration(data,soup):
    if (data['terminationAttachment'] is not None) and (len(data['terminationAttachment'])!=0):
        soup.findAll(attrs={'class':'base-title'})[4].string.replace_with('终止审核通知')
        tempsoup = soup.findAll(attrs={'class':'info-disc-table'})[3].findAll('tbody')[0]
        length = len(data['terminationAttachment'])
        for i in range(length):
                new_soup = BeautifulSoup('<tr><td></td><td><a target="_blank"></td><td class="text_center">\
    </td></tr>', 'html.parser')
                new_soup.a.string = data['terminationAttachment'][i]['ftitle']
                new_soup.a['href'] = './'+data['baseInfo']['cmpName']+ '/'+ \
    data['terminationAttachment'][i]['fname']
                new_soup.td.string = str(i+1)
                new_soup.find(attrs={'class':'text_center'}).string = data['terminationAttachment'][i]['fdate']
                tempsoup.append(new_soup)
    else:
        tempsoup = soup.findAll(attrs={'class':'info-disc-table'})[3].findAll('tbody')[0]
        length = len(data['registrationAttachment'])
        if length ==0:
            new_soup = BeautifulSoup('<tr style="border:none;"><td colspan="10"><div class="report-nodata">\
    <span class="nodata-text">暂无数据！</span></div></td></tr>','html.parser')
            tempsoup.append(new_soup)
        else:
            for i in range(length):
                new_soup = BeautifulSoup('<tr><td></td><td><a target="_blank"></td><td class="text_center">\
    </td></tr>', 'html.parser')
                new_soup.a.string = data['registrationAttachment'][i]['ftitle']
                new_soup.a['href'] = './'+data['baseInfo']['cmpName']+ '/'+ \
    data['registrationAttachment'][i]['fname']
                new_soup.td.string = str(i+1)
                new_soup.find(attrs={'class':'text_center'}).string = data['registrationAttachment'][i]['fdate']
                tempsoup.append(new_soup)

def generate_others(data,soup):
    tempsoup = soup.findAll(attrs={'class':'info-disc-table'})[4].findAll('tbody')[0]
    if data['others'] is None:
        new_soup = BeautifulSoup('<tr style="border:none;"><td colspan="10"><div class="report-nodata">\
<span class="nodata-text">暂无数据！</span></div></td></tr>','html.parser')
        tempsoup.append(new_soup)
    else:
        length = len(data['others'])
        for i in range(length):
            new_soup = BeautifulSoup('<tr><td></td><td><a target="_blank"></td><td class="text_center">\
</td></tr>', 'html.parser')
            new_soup.a.string = data['others'][i]['reason']
            new_soup.td.string = str(i+1)
            new_soup.find(attrs={'class':'text_center'}).string = data['others'][i]['date']
            tempsoup.append(new_soup)


# def progressBar(data,soup):
#     tempsoup = soup.find(attrs={'class':'project-dy-flow-con'})
#     # stage = ['已受理','已问询','上市委会议','提交注册','注册结果']
#     # stagenum = stage.index(data['prjst'])
#     # for i in range(5):
#     # projMilestone
#     profile = json.loads(data['pjdot'])
#     stage = [profile[p]['name'] for p in profile.keys() if p != '-1']
#     stagenum = stage.index(data['prjprog'])
#     for i in range(len(stage)):
#         if i < stagenum:
#         # width 应该是 100/len(stage)
#             finish_soup = BeautifulSoup('<li class="finished" style="width:20%;min-width:14%"><b>\
# <span class="title"></span><span class="date"></span></b></li>','html.parser')
#             finish_soup.find(attrs={'class':'title'}).string = stage[i]
#             date,_ = profile[str(i)]['startTime'].split(' ')
#             finish_soup.find(attrs={'class':'date'}).string= date
#             tempsoup.append(finish_soup)
#         if i==stagenum:
#             dealing_soup = BeautifulSoup('<li class="dealing" style="width:20%;min-width:14%"><b>\
# <span class="title"></span><span class="date"></span></b><span class="other-style"><span></span></span></li>','html.parser')
#             dealing_soup.find(attrs={'class':'title'}).string = stage[i]
#             date,_ =profile[str(i)]['startTime'].split(' ')
#             dealing_soup.find(attrs={'class':'date'}).string= date
#             tempsoup.append(dealing_soup)
#         elif i > stagenum:
#             pending_soup = BeautifulSoup('<li class="pengding" style="width:20%;min-width:14%"><b>\
# <span class="title"></span><span class="date"></span></b></li>','html.parser')
#             pending_soup.find(attrs={'class':'title'}).string = stage[i]
#             tempsoup.append(pending_soup)

def save_html(soup,directory):
    # saved_path = r'C:\Users\chen\Desktop\测试网页' +'\\'+ data['baseInfo']['cmpName']+ '.html'
    
    with open (directory,"w", encoding='utf-8') as f:
    #   写文件用bytes而不是str，所以要转码  
        f.write(str(soup))


def gen_html(data):
    template_path = r'C:\Users\chen\Desktop\IPO_info\template\创业板发行上市审核信息公开网站-IPO详情.html'
    soup = load_template(template_path)
    generate_info(data,soup)
    generate_release(data,soup)
    generate_response(data,soup)
    generate_meeting(data,soup)
    generate_registration(data,soup)
    generate_others(data,soup)
    generate_title(data,soup)
    # progressBar(data,soup)
    if data['baseInfo']['auditMarket'] == '上交所':
        saved_path = os.getcwd() + '/data/IPO/科创板/'+ data['baseInfo']['cmpName']+ '/' + data['baseInfo']['cmpName'] +'.html'
    else:
        saved_path = os.getcwd() + '/data/IPO/创业板/'+ data['baseInfo']['cmpName']+ '/' + data['baseInfo']['cmpName'] +'.html'
    save_html(soup,saved_path)
    print("Success! {} HTML generated.".format(data['baseInfo']['cmpName']))
    
    # progressBar(data,soup)
    return 

if __name__ == '__main__':
    template_path = r'C:\Users\chen\Desktop\测试网页\创业板发行上市审核信息公开网站-IPO详情.html'
    d = os.getcwd()
    directories = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
    for direc in directories:
        cmpName = os.path.basename(direc)
        if cmpName == '创业板发行上市审核信息公开网站-IPO详情_files':
            continue
        data_path = os.getcwd() +'/data/IPO/创业板/' + cmpName + '/clean_info.pkl'
        data = load_pickle(data_path)
        soup = load_template(template_path)
        html = gen_html(data,soup)
    # progressBar(data,soup)
        saved_path = os.getcwd() + '/'+  cmpName + '/'+ cmpName +'.html'
        save_html(html,saved_path)
        print("Success! {} HTML generated.".format(cmpName))
    # data_path = r'C:\Users\chen\Desktop\IPO_info\三生国健药业（上海）股份有限公司\clean_info.pkl'
    # data =load_pickle(data_path)
    # soup = load_template(template_path)
    # html = gen_html(data,soup)
    # saved_path = r'C:\Users\chen\Desktop\测试网页' +'\\'+ data['baseInfo']['cmpName']+ '.html'
    # save_html(html,saved_path)
    # print("Success! {} HTML generated.".format(data['baseInfo']['cmpName']))