def update_alert():
    proj_list_new = index_getter()
    proj_list_old = load_obj('C:/Users/chen/Desktop/IPO_info/sh_index')
    for i in 

def status_update():
    updated_idx = [index for (index, d) in enumerate(proj_list_new) if d["updtdt"] == datetime.today().strftime('%Y-%m-%d')]
    for new_idx in updated_idx:
        name,projid = proj_list_new[i]['cmpnm'],proj_list_new[i]['prjid']
        old_idx = next((index for (index, d) in enumerate(proj_list_old) if d["cmpnm"] == name), None)
        # for key, value in proj_list_new[i].items():
        #     if proj_list_old[old_index][key] != value:
        #         print(key,value,proj_list_old[old_index][key])
        if proj_list_new[new_idx]['prjst'] != proj_list_old[old_idx]['prjst']:
            data_getter(proj_list_new[new_idx]['prjid'])


def new_project():
        for i in list_1:
            if i not in list_2:
            print(i)
    