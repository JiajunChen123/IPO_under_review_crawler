import datetime

def check_update():
    prjtypes = ['ipo','refinance','reproperty']
    for prjtype in prjtypes:
    proj_list_new = index_getter(prjtype)
    proj_list_old = load_pickle(os.getcwd()+'/saved_config/sz_index'+'_'+'prjtype'+'.pkl')

    updated_idx = [index for (index, d) in enumerate(proj_list_new) if d["updtdt"] == datetime.today().strftime('%Y-%m-%d')]
    print("there are {} projects have been updated!")
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
        print('company:', os.path.dirname(i),'is updated')

