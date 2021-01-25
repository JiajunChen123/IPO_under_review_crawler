import datetime
import os
from preprocessing import data_process
from sz_IPO_crawler import data_getter, index_getter
from utils import load_pickle,save_pickle

def check_update():
    prjtypes = ['ipo','refinance','reproperty']
    for prjtype in prjtypes:
        try: 
            proj_list_old = load_pickle(os.getcwd()+'/saved_config/sz_index'+'_'+'prjtype'+'.pkl')
            
        except:
        else:




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
        save_pickle(allStock_info, saved_path)
    return 

