def update_alert():
    proj_list_new = index_getter()
    proj_list_old = load_obj('C:/Users/chen/Desktop/IPO_info/sh_index')
    for i in 

def status_update():
    updated_idx = [index for (index, d) in enumerate(proj_list_new) if d["updtdt"] == datetime.today().strftime('%Y-%m-%d')]

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


def new_project(proj_list_new,proj_list_old):
    for i in list_1:
        if i['prjid'] not in list_2:
        print(i)
