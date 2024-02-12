import json
with open('/home/will/dissertation/sort_times/always_insert_update_bonus.json', 'r') as f:
    data = json.load(f)
    for idx, i in enumerate(data['radix_sort']):
        for j in [12,16]:
            data['radix_sort'][idx]['times'][f'msd_p_{j}_always_insert_update'] = i['times'][f'msd_p_14_always_insert_update']
            
with open('/home/will/dissertation/sort_times/always_insert_update_bonus.json', 'w') as f:
    json.dump(data, f, indent=4)