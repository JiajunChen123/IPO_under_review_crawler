import datetime
import os
from Preprocessing import load_pickle
from sz_IPO_crawler import data_getter, index_getter
def check_update():
    prjtypes = ['ipo','refinance','reproperty']
    for prjtype in prjtypes:
        proj_list_new = index_getter(prjtype)
        proj_list_old = load_pickle(os.getcwd()+'/saved_config/sz_index'+'_'+'prjtype'+'.pkl')

        updated_idx = [index for (index, d) in enumerate(proj_list_new) if d["updtdt"] == datetime.today().strftime('%Y-%m-%d')]
        print("there are {} projects have been updated!".format(len(updatedidx)))
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
            directory = os.getcwd()+'/data/'+cleaned_data['prjType'] + '/' + cleaned_data['prjName']
            save_obj(cleaned_data, directory +'/clean_info')
            print('company:', cleaned_data['prjName'],'is updated')


def update_allStockInfo():
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()+'/data/IPO/'):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    allStock_info = []
    for i in listOfFiles:
        if os.path.basename(i) == 'clean_info.pkl':
            # print('clean up company:', os.path.dirname(i))
            # raw_data = load_pickle(i)
            # cleaned_data = data_process(raw_data)
            clean_data = load_pickle(i)
            allStock_info.append(cleaned_data)
            saved_path = os.getcwd()+'/saved_config/'+'IPO_stocksInfo'
            save_obj(allStock_info, saved_path)
            print('clean up company:', os.path.dirname(i))
    to_dataframe(allStock_info)
    save_obj(allStock_info, saved_path)
    return update_allStockInfo