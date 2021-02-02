'''
temp_dict ={'baseInfo':baseInfo,                # 项目基本信息
            'disclosureMaterial':[fileConfig],            # 信息披露
            'responseAttachment':[fileConfig],            # 问询与回复
            'meetingAttachment':[fileConfig],             # 上市委会议公告与结果
            'terminationAttachment':[fileConfig],         # 终止审核通知
            'registrationAttachment':[fileConfig],       # 注册结果通知
            'others':[others]}                        # 其他


baseInfo = {'projID':'',                        # 项目id
            'cmpName':'',                       # 公司名称
            'cmpAbbrname':'',                   # 公司简称
            'projType':'',                      # 项目类型
            'currStatus':'',                    # 审核状态
            'region':'',                        # 所属地区
            'csrcCode':'',                      # 所属行业
            'acptDate':'',                      # 受理日期
            'updtDate':'',                      # 更新日期
            'issueAmount':'',                   # 融资金额
            'sprInst':'',                       # 保荐机构
            'sprInstAbbr':'',                   # 保荐机构简称
            'sprRep':'',                        # 保荐代表人
            'acctFirm':'',                      # 会计师事务所
            'acctSgnt':'',                      # 签字会计师
            'lawFirm':'',                       # 律师事务所
            'lglSgnt':'',                       # 签字律师
            'evalSgnt':'',                      # 签字评估师
            'evalInst':'',                      # 评估机构
            'projMilestone':[projMilestone],      # 项目里程碑
            'auditMarket':''}                   # 所属交易所


projMilestone = {'1':{'status':'已受理',
                      'time':'',
                      'result':''},
                '2':{'status':'已问询',
                        'result':'',
                      'time':''},
                '3':{'status':'上市委会议',
                    'result':'',
                      'time':''},            
                '4':{'status':'提交注册',
                      'result':'',
                      'time':''},            
                '5':{'status':'注册结果',
                      'result':'',
                      'time':''}}          #           #

fileConfig = {  'fname':'',                 #  文件名
                'ftype':'',                 #  文件所属类型   
                'fphynm':'',                #  文件唯一识别名
                'ftitle':'',                #  文件标题
                'fstatus':'',               #  文件所属环节
                'fdate':'',                 #  文件日期
                'fpath':'',                 #  文件地址
                'fext':'',                  #  文件后缀
                'other':''}                 #   (待选)

others = {  'index':'',
            'reason':'',
            'date':'',
            'timestamp':''}

temp_dict ={'baseInfo':baseInfo,                # 项目基本信息
            'disclosureMaterial':[fileConfig],            # 信息披露
            'responseAttachment':[fileConfig],            # 问询与回复
            'meetingAttachment':[fileConfig],             # 上市委会议公告与结果
            'terminationAttachment':[fileConfig],         # 终止审核通知
            'registrationAttachment':[fileConfig],       # 注册结果通知
            'others':[others]}                        # 其他
'''

import json
import os
import pickle
from utils import load_pickle,save_pickle

def data_process(raw_data):
    '''
    input : raw_data : dict
    '''
    if 'prjid' in raw_data:
        # this is from sz_exchange
        cleaned_data = sz_process(raw_data)
        directory = os.getcwd() + '/data/IPO/创业板/' + cleaned_data['baseInfo']['cmpName'] 
        save_pickle(cleaned_data, directory + '/' + 'clean_info.pkl')
    else:
        cleaned_data = sh_process(raw_data)
        directory = os.getcwd() + '/data/IPO/科创板/' + cleaned_data['baseInfo']['cmpName'] 
        save_pickle(cleaned_data, directory + '/' + 'clean_info.pkl')
    return cleaned_data


def sz_process(raw_data):
    cleaned_dict = {}
    temp = json.loads(raw_data['pjdot'])
    
    milestone =[]
    for i in temp.keys():
        if i != '-1' and temp[i]['startTime'] is not None:
            temp_dict= {'status':temp[i]['name'],'date':temp[i]['startTime'].split(' ')[0],'result':''}
            milestone.append(temp_dict)
    if '-1' in temp.keys():
        milestone[-1]['result'] = temp['-1']['name']

    # clean up info 
    cleaned_dict['baseInfo'] = {'projID':raw_data['prjid'],                        # 项目id
            'cmpName':raw_data['cmpnm'],                       # 公司名称
            'cmpAbbrname':raw_data['cmpsnm'],                   # 公司简称
            'projType':raw_data['biztyp'],                      # 项目类型
            'currStatus':raw_data['prjst'],                    # 审核状态
            'region':raw_data['regloc'],                        # 所属地区
            'csrcCode':raw_data['csrcind'],                      # 所属行业
            'acptDate':raw_data['acptdt'],                      # 受理日期
            'updtDate':raw_data['updtdt'],                      # 更新日期
            'issueAmount':raw_data['maramt'],                   # 融资金额
            'sprInst':raw_data['sprinst'],                       # 保荐机构
            'sprInstAbbr':raw_data['sprinsts'],                   # 保荐机构简称
            'sprRep':raw_data['sprrep'],                        # 保荐代表人
            'acctFirm':raw_data['acctfm'],                      # 会计师事务所
            'acctSgnt':raw_data['acctsgnt'],                      # 签字会计师
            'lawFirm':raw_data['lawfm'],                       # 律师事务所
            'lglSgnt':raw_data['lglsgnt'],                       # 签字律师
            'evalSgnt':raw_data['evalinst'],                      # 签字评估师
            'evalInst':raw_data['evalsgnt'],                      # 评估机构
            'projMilestone':milestone,      # 项目里程碑
            'auditMarket':'深交所'}                   # 所属交易所

    # clean up file
    indicator = {'disclosureMaterials':'disclosureMaterial',
                'enquiryResponseAttachment':'responseAttachment',
                'meetingConclusionAttachment':'meetingAttachment',
                'terminationNoticeAttachment':'terminationAttachment',
                'registrationResultAttachment':'registrationAttachment'}

    for key,value in indicator.items():
        material =[]
        for file in raw_data[key]:
            temp_dict =  { 'fname':file['dfnm'],           #  文件名
                    'ftype':file['matnm'],                 #  文件所属类型   
                    'fphynm':file['dfphynm'],              #  文件唯一识别名
                    'ftitle':file['dftitle'],              #  文件标题
                    'fstatus':file['type'],                #  文件所属环节
                    'fdate':file['ddt'],                   #  文件日期
                    'fpath':file['dfpth'],                 #  文件地址
                    'fext':file['dfext'],                  #  文件后缀
                    'other':''} 
            material.append(temp_dict)
        cleaned_dict[value] = material

    # clean up others 
    idx = 1
    temp2 = []
    if raw_data['others'] is not None:
        for item in raw_data['others']:

            others = {  'order':idx,
                'reason':list(item.values())[0].split()[0],
                'date':list(item.keys())[0].split()[0],
                'timestamp':list(item.keys())[0].split()[1]}
            idx+=1
            temp2.append(others)
        cleaned_dict['others'] = temp2
    else:
        cleaned_dict['others'] = ''
    return cleaned_dict


def sh_process(raw_data):
    cleaned_dict = {}
    # temp = json.loads(raw_data['pjdot'])
    name_list = ['已受理', '已问询', '上市委会议', '提交注册', '注册生效','','中止（财报更新）','终止']
    milestone = []

    for st in raw_data['status']:
        if st['suspendStatus'] != '':
            continue
        commit_result = '通过' if st['commitiResult'] == 1 else ''
        temp_dict = {
            'status': name_list[st['auditStatus'] - 1],
            'date': st['publishDate'],
            'result': commit_result
        }
        milestone.append(temp_dict)

    info = raw_data['info'][0]

    numInst = len(info['intermediary'])
    sx = info['intermediary'][0]['i_person'] if numInst > 0 else ''
    k = [
        ssx['i_p_personName'] for ssx in sx
        if ssx['i_p_jobType'] == 22 or ssx['i_p_jobType'] == 23
    ]

    sprrep = ', '.join(k)
    sx = info['intermediary'][1]['i_person'] if numInst > 1 else ''
    k = [
        ssx['i_p_personName'] for ssx in sx
        if ssx['i_p_jobType'] == 32 or ssx['i_p_jobType'] == 33
    ]
    acctfirm = info['intermediary'][1]['i_intermediaryName'] if numInst > 1 else ''
    acctsgnt = ', '.join(k)
    sx = info['intermediary'][2]['i_person'] if numInst > 2 else ''
    k = [
        ssx['i_p_personName'] for ssx in sx
        if ssx['i_p_jobType'] == 42 or ssx['i_p_jobType'] == 43
    ]
    lawfirm = info['intermediary'][2]['i_intermediaryName'] if numInst > 2 else ''
    lglsgnt = ', '.join(k)
    sx = info['intermediary'][3]['i_person'] if numInst > 3 else ''
    k = [
        ssx['i_p_personName'] for ssx in sx
        if ssx['i_p_jobType'] == 52 or ssx['i_p_jobType'] == 53
    ]
    evalinst = info['intermediary'][3]['i_intermediaryName'] if numInst > 3 else ''
    evalsgnt = ', '.join(k)
    # clean up info
    cleaned_dict['baseInfo'] = {
        'projID': info['stockAuditNum'],  # 项目id
        'cmpName': info['stockIssuer'][0]['s_issueCompanyFullName'],  # 公司名称
        'cmpAbbrname':
        info['stockIssuer'][0]['s_issueCompanyAbbrName'],  # 公司简称
        'projType': 'IPO',  # 项目类型
        'currStatus': name_list[info['currStatus'] - 1],  # 审核状态
        'region': info['stockIssuer'][0]['s_province'],  # 所属地区
        'csrcCode': info['stockIssuer'][0]['s_csrcCodeDesc'],  # 所属行业
        'acptDate': raw_data['status'][0]['publishDate'],  # 受理日期
        'updtDate': raw_data['status'][-1]['publishDate'],  # 更新日期
        'issueAmount': info['planIssueCapital'],  # 融资金额
        'sprInst': info['intermediary'][0]['i_intermediaryName'],  # 保荐机构
        'sprInstAbbr':
        info['intermediary'][0]['i_intermediaryAbbrName'],  # 保荐机构简称
        'sprRep': sprrep,  # 保荐代表人
        'acctFirm':  acctfirm,  # 会计师事务所
        'acctSgnt': acctsgnt,  # 签字会计师
        'lawFirm': lawfirm,  # 律师事务所
        'lglSgnt': lglsgnt,  # 签字律师
        'evalSgnt': evalsgnt,  # 签字评估师
        'evalInst': evalinst,  # 评估机构
        'projMilestone': milestone,  # 项目里程碑
        'auditMarket': '上交所'
    }  # 所属交易所

    disclosureMaterial= []
    responseAttachment = []
    meetingAttachment = []
    terminationAttachment = []
    registrationAttachment = []
    for file in raw_data['release']:

        temp_dict = {
            'fname': file['fileTitle'],  #  文件名
            'ftype': '',  #  文件所属类型   
            'fphynm': file['filename'],  #  文件唯一识别名
            'ftitle': file['fileTitle'],  #  文件标题
            'fstatus': '',  #  文件所属环节
            'fdate': file['publishDate'],  #  文件日期
            'fpath': file['filePath'],  #  文件地址
            'fext': '',  #  文件后缀
            'other': ''
        }
        if file['fileType'] == 30:
            disclosureMaterial.append(temp_dict)
            temp_dict['ftype'] = '招股说明书'
            temp_dict['fstatus'] = file['auditStatus']
        elif file['fileType'] == 36:
            disclosureMaterial.append(temp_dict)
            temp_dict['ftype'] = '发行保荐书'
            temp_dict['fstatus'] = file['auditStatus']
        elif file['fileType'] == 37:
            disclosureMaterial.append(temp_dict)
            temp_dict['ftype'] = '上市保荐书'
            temp_dict['fstatus'] = file['auditStatus']
        elif file['fileType'] == 32:
            disclosureMaterial.append(temp_dict)
            temp_dict['ftype'] = '审计报告'
            temp_dict['fstatus'] = file['auditStatus']
        elif file['fileType'] == 33:
            disclosureMaterial.append(temp_dict)
            temp_dict['ftype'] = '法律意见书'
            temp_dict['fstatus'] = file['auditStatus']
        elif file['fileType'] == 6:
            responseAttachment.append(temp_dict)
        elif file['fileType'] == 5:
            responseAttachment.append(temp_dict)
        elif file['fileType'] == 35:
            registrationAttachment.append(temp_dict)
        elif file['fileType'] == 38:
            terminationAttachment.append(temp_dict)

    for file in raw_data['result']:
        temp_dict = {
            'fname': file['fileTitle'],  #  文件名
            'ftype': '',  #  文件所属类型   
            'fphynm': file['fileName'],  #  文件唯一识别名
            'ftitle': file['fileTitle'],  #  文件标题
            'fstatus': '',  #  文件所属环节
            'fdate': file['publishDate'],  #  文件日期
            'fpath': file['filePath'],  #  文件地址
            'fext': '',  #  文件后缀
            'other': ''
        }
        if file['fileType'] == 1 or file['fileType'] == 2:
            meetingAttachment.append(temp_dict)
    cleaned_dict['disclosureMaterial'] = disclosureMaterial
    cleaned_dict['responseAttachment'] = responseAttachment
    cleaned_dict['meetingAttachment'] = meetingAttachment
    cleaned_dict['terminationAttachment'] = terminationAttachment
    cleaned_dict['registrationAttachment'] = registrationAttachment

    idx = 1
    temp2 = []
    if raw_data['res'] is not None:
        for item in raw_data['res']:
            if item['reasonDesc'] != '':
                others = {
                    'order': idx,
                    'reason': item['reasonDesc'],
                    'date': item['publishDate'],
                    'timestamp': item['timesave'].split(' ')[1]
                }
                idx += 1
                temp2.append(others)
        cleaned_dict['others'] = temp2
    else:
        cleaned_dict['others'] = ''
    return cleaned_dict




# if __name__ == '__main__':
#     # listOfFiles = list()
#     # for (dirpath, dirnames, filenames) in os.walk(os.getcwd()):
#     #     listOfFiles += [os.path.join(dirpath, file) for file in filenames]
#     # allStock_info = []
#     # for i in listOfFiles:
#     #     if os.path.basename(i) == 'info.pkl':
#     #         print('clean up company:', os.path.dirname(i))
#     #         raw_data = load_pickle(i)
#     #         cleaned_data = data_process(raw_data)
#     #         allStock_info.append(cleaned_data)
#     #         save_obj(cleaned_data, os.path.dirname(i), 'clean_info')
#     #         print('clean up company:', os.path.dirname(i))
#     # to_dataframe(allStock_info)
#     # save_obj(allStock_info, os.getcwd(), 'allStock_info')
#     # allStock_info = load_pickle('allStock_info.pkl')
#     # to_html(allStock_info)