import json 

def process_data(args):
    with open(file_path, 'r', encoding='utf-8') as file:
        data_list = json.load(file)

    print(len(data_list))
    
    # Standardize the dictionary data structure.
    for d in data_list: 
        for g_t in d['response'].keys():
            if 'slot' in d['response'][g_t]:
                d['response'][g_t] = d['response'][g_t]['slot']
            elif 'slots' in d['response'][g_t]:
                d['response'][g_t] = d['response'][g_t]['slots']

    for d in data_list:
        for g_t, states in d['states'].items():
            home_score, away_score = states['cumulative_score'].split(', ')
            states['cumulative_score'] = {'home' : int(home_score), 'away' : int(away_score)}
                
    for d in data_list:
        for g_t in d['response'].keys():
            for k in ['home_goal', 'home_shots_on_Target', 'home_yellow_card', 'home_red_card', 'home_assist', 'home_sub_in', 'home_sub_out', 'away_goal', 'away_shots_on_Target', 'away_yellow_card', 'away_red_card', 'away_assist', 'away_sub_in', 'away_sub_out', 'cumulative_score']:
                if k not in d['response'][g_t]:
                    d['response'][g_t][k] = ''

    for d in data_list:
        for g_t in d['response'].keys():
            for k in list(d['response'][g_t].keys()):
                if k not in ['home_goal', 'home_shots_on_Target', 'home_yellow_card', 'home_red_card', 'home_assist', 'home_sub_in', 'home_sub_out', 'away_goal', 'away_shots_on_Target', 'away_yellow_card', 'away_red_card', 'away_assist', 'away_sub_in', 'away_sub_out', 'cumulative_score']:
                    del d['response'][g_t][k] 

    for d in data_list:
        for g_t, states in d['response'].items():
            for k, k_new in zip(['away_shots_on_Target','away_sub_in','away_sub_out','home_shots_on_Target','home_sub_in','home_sub_out'], ['home_swap_out','away_swap_out','away_swap_in','home_Shoots_on_Target','away_Shoots_on_Target','home_swap_in']):
                states[k_new] = states[k]
                del states[k]
            for k, v in states.items():
                if k == 'cumulative_score':
                    continue
                else :
                    if isinstance(v,list):
                        continue
                    if v == None:
                        states[k] = []
                    else :
                        states[k] = [player.strip() for player in v.split(',')]

    with open(args.save_file_path, 'w', encoding='utf-8')as file :
        json.dump(data_list, file,indent=4,ensure_ascii=False)





if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file_path', type=str)
    parser.add_argument('--save_file_path', type=str)
    args = parser.parse_args()
    
    process_data(args)
    pass