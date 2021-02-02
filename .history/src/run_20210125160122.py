import datetime
import os
from preprocessing import data_process
from sz_IPO_crawler import data_getter, index_getter
from utils import load_pickle,save_pickle
import random,time
from html_gen import gen_html



def check_update():
    prjtypes = ['ipo','refinance','reproperty']
    for prjtype in prjtypes:
        try: 
            proj_list_old = load_pickle(os.getcwd()+'/saved_config/sz_index'+'_'+prjtype+'.pkl')
            proj_list_new = index_getter(prjtype)
            stocksInfo = load_pickle(os.getcwd()+'/saved_config/'+prjtype+'_stocksInfo.pkl')
            updated_idx = [index for (index, d) in enumerate(proj_list_new) if d["updtdt"] == datetime.today().strftime('%Y-%m-%d')]
            if updated_idx == []:
                print("Nothing has changed!")
                r
            else:
                print("there are {} projects have been updated!".format(len(updated_idx)))
                for new_idx in updated_idx:
                    # name,projid = proj_list_new[i]['cmpnm'],proj_list_new[i]['prjid']
                    # old_idx = next((index for (index, d) in enumerate(proj_list_old) if d["cmpnm"] == name), None)
                    # if old_idx is not None:
                    # # for key, value in proj_list_new[i].items():
                    # #     if proj_list_old[old_index][key] != value:
                    # #         print(key,value,proj_list_old[old_index][key])
                    # if proj_list_new[new_idx]['prjst'] != proj_list_old[old_idx]['prjst']:
                    raw_data = data_getter(proj_list_new[new_idx]['prjid'])
                    cleaned_data = data_process(raw_data)
                    html = gen_html(cleaned_data)
                    print('company:', cleaned_data['prjName'],'is updated')
        except FileNotFoundError:
            proj_list = index_getter(prjtype)
            print('there are total {} stocks in the list'.format(len(proj_list)))
            i=0
            for proj in proj_list:
                i+=1
                print('fetching {} project, {}'.format(i,proj['cmpsnm']))
                stockInfo = data_getter(str(proj['prjid']))
                cleaned_data = data_process(stockInfo)
                html = gen_html(cleaned_data)
                # file_getter(stockInfo)
                time.sleep(random.randint(2,5))
            print('Update completed!!!!')




def update_allStockInfo():
    prjtypes = ['IPO','再融资','资产重组']
    for prjtype in prjtypes:
        listOfFiles = list()
        for (dirpath, dirnames, filenames) in os.walk(os.getcwd()+'/data/'+prjtype):
            listOfFiles += [os.path.join(dirpath, file) for file in filenames]
        allStock_info = []
        for i in listOfFiles:
            if os.path.basename(i) == 'clean_info.pkl':
                # print('clean up company:', os.path.dirname(i))
                # raw_data = load_pickle(i)
                # cleaned_data = data_process(raw_data)
                clean_data = load_pickle(i)
                allStock_info.append(clean_data)
                saved_path = os.getcwd()+'/saved_config/'+prjtype+'_stocksInfo.pkl'
                print('clean up company:', os.path.dirname(i))
        # to_dataframe(allStock_info)
        saved_path = os.getcwd()+'/saved_config/'+prjtype+'_stocksInfo.pkl'
        save_pickle(allStock_info, saved_path)
    return 

