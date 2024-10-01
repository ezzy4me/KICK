import argparse
import json
def compare_B(B_true, B_pred):
    total_slot = len(B_pred)
    score_hit = 0
    total_hit = 0
    slot_hit = 0
    for k in B_true.keys():
        if k not in B_pred : 
            continue
        if k =='cumulative_score':
            if B_true[k] == B_pred[k]:
                score_hit += 1
                total_hit += 1
                slot_hit += 1
            continue
        if set(B_true[k]) == set(B_pred[k]):
            total_hit += 1

    return total_slot, score_hit, total_hit

def compare_slot(B_true, B_pred):
    slots = len(B_pred)
    slot_hits = 0
    unique_slots = 0
    unique_slot_hits = 0
    for k in B_pred.keys():
        if k == 'cumulative_score':
            slot_hits += 1
            unique_slot_hits += 1
            unique_slots += 1
            continue
        elif (B_pred[k] != [] and B_true[k] != []): # 둘 다 값이 있다고 예측
            slot_hits += 1
            unique_slots += 1
            unique_slot_hits += 1
        elif (B_pred[k] == [] and B_true[k] == []): # 둘 다 빈칸으로 예측
            slot_hits += 1
        elif B_pred[k] != [] or B_true[k] != []: # 하나의 값만 빈칸
            unique_slots += 1
    return slot_hits, slots, unique_slot_hits, unique_slots

def calculate_JGA(game):
    # jga_hit = 0
    jga_hit = 1
    if len(game['response']) == 0:
        return -1
    for game_time in game['response'].keys():
        total_slot, score_hit, total_hit = compare_B(game['states'][game_time], game['response'][game_time])
        # game_total += total_slot
        # game_score_total += score_hit
        # game_total_hit += total_hit
        # game_slot_hit += slot_hit
        if total_hit == total_slot:
            jga_hit+=1
            
        else : 
            break
    return jga_hit / len(game['response'].keys())

def calculate_TGA(game):
    # jga_hit = 0
    tga_hit = 1
    if len(game['response']) == 0:
        return -1
    for game_time in game['response'].keys():
        total_slot, _, total_hit = compare_B(game['states'][game_time], game['response'][game_time])
        # game_total += total_slot
        # game_score_total += score_hit
        # game_total_hit += total_hit
        # game_slot_hit += slot_hit
        if total_hit == total_slot:
            tga_hit+=1
    return tga_hit / len(game['response'].keys())




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file_path', type=str)
    args = parser.parse_args()

    with open(args.data_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # JGA 
    total_JGA_scores = 0
    total_TGA_scores = 0
    total_RGI_scores = 0
    total_game_num = len(data)
    for game in data:
        jga_score = calculate_JGA(game)
        tga_score = calculate_TGA(game)
        if jga_score == -1:
            total_game_num -= 1
            continue

        total_JGA_scores += jga_score
        total_TGA_scores += tga_score
        total_RGI_scores +=  1 - ((tga_score -jga_score) / (tga_score+jga_score))
    print(f"JGA : {total_JGA_scores} / {total_game_num} : {total_JGA_scores / total_game_num}")
    print(f"TGA : {total_TGA_scores} / {total_game_num} : {total_TGA_scores / total_game_num}")
    print(f"RGI : {total_RGI_scores} / {total_game_num} : {total_RGI_scores / total_game_num}")


    # SA
    total_SA_scores = 0
    total_game_num = len(data)
    for game in data:
        game_slot_hits = 0
        game_slots = 0 
        if len(game['response'].keys()) == 0:
            total_game_num -= 1
            continue
        for game_time in game['response'].keys():
            slot_hits, slots , unique_slot_hits, unique_slots = compare_slot(game['states'][game_time], game['response'][game_time])
            game_slot_hits += slot_hits
            game_slots += slots
        game_sa = game_slot_hits / game_slots
        total_SA_scores += game_sa
    print(f"SA : {total_SA_scores} / {total_game_num} : {total_SA_scores / total_game_num}")

    # RSA
    total_RSA_scores = 0
    total_game_num = len(data)
    for game in data:
        game_unique_slot_hits = 0
        game_unique_slots = 0 
        if len(game['response'].keys()) == 0:
            total_game_num -= 1
            continue
        for game_time in game['response'].keys():
            slot_hits, slots , unique_slot_hits, unique_slots = compare_slot(game['states'][game_time], game['response'][game_time])
            game_unique_slot_hits += unique_slot_hits
            game_unique_slots += unique_slots
        game_rsa = game_unique_slot_hits / game_unique_slots
        total_RSA_scores += game_rsa
    print(f"RSA : {total_RSA_scores} / {total_game_num} : {total_RSA_scores / total_game_num}")


    # half only 
    print("---------------half only----------------")
    for game in data:
        new_game_states = { }
        for k in game['states'].keys():
            if 'first' in k:
                new_game_states[k] = game['states'][k]
        new_game_response = {}
        for k in game['response'].keys():
            if 'first' in k:
                new_game_response[k] = game['response'][k]
        game['states'] = new_game_states
        game['response'] = new_game_response

    # JGA 
    total_JGA_scores = 0
    total_TGA_scores = 0
    total_RGI_scores = 0
    total_game_num = len(data)
    for game in data:
        
        jga_score = calculate_JGA(game)
        tga_score = calculate_TGA(game)
        if jga_score == -1:
            total_game_num -= 1
            continue

        total_JGA_scores += jga_score
        total_TGA_scores += tga_score
        total_RGI_scores +=  1 - ((tga_score -jga_score) / (tga_score+jga_score))
    print(f"JGA : {total_JGA_scores} / {total_game_num} : {total_JGA_scores / total_game_num}")
    print(f"TGA : {total_TGA_scores} / {total_game_num} : {total_TGA_scores / total_game_num}")
    print(f"RGI : {total_RGI_scores} / {total_game_num} : {total_RGI_scores / total_game_num}")


    # SA
    total_SA_scores = 0
    total_game_num = len(data)
    for game in data:
        game_slot_hits = 0
        game_slots = 0 
        if len(game['response'].keys()) == 0:
            total_game_num -= 1
            continue
        for game_time in game['response'].keys():
            slot_hits, slots , unique_slot_hits, unique_slots = compare_slot(game['states'][game_time], game['response'][game_time])
            game_slot_hits += slot_hits
            game_slots += slots
        game_sa = game_slot_hits / game_slots
        total_SA_scores += game_sa
    print(f"SA : {total_SA_scores} / {total_game_num} : {total_SA_scores / total_game_num}")

    # RSA
    total_RSA_scores = 0
    total_game_num = len(data)
    for game in data:
        game_unique_slot_hits = 0
        game_unique_slots = 0 
        if len(game['response'].keys()) == 0:
            total_game_num -= 1
            continue
        for game_time in game['response'].keys():
            slot_hits, slots , unique_slot_hits, unique_slots = compare_slot(game['states'][game_time], game['response'][game_time])
            game_unique_slot_hits += unique_slot_hits
            game_unique_slots += unique_slots
        game_rsa = game_unique_slot_hits / game_unique_slots
        total_RSA_scores += game_rsa
    print(f"RSA : {total_RSA_scores} / {total_game_num} : {total_RSA_scores / total_game_num}")
