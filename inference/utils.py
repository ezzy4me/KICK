import requests
import json

def truncate_chat(input_list):
    # Initialize variables to hold the total content length and processed list
    total_length = 0
    processed_list = []
    is_truncated = False

    # Iterate over the list in reverse to check total content length and adjust if needed
    for item in reversed(input_list):
        current_content_length = len(item['content'])
        if total_length + current_content_length > 5000:
            is_truncated = True
            break  # Skip adding this item to the processed list  
        processed_list.insert(0, item)  # Add the item at the beginning of the list
        total_length += current_content_length
    if processed_list[0]['role'] == 'model':
        processed_list = processed_list[1:]
    return is_truncated, processed_list


def generate_content(chat_list, data_type = 'default'):
    chat_list_filtered = []
    if data_type == "default":
        chat_list_filtered = chat_list
    elif data_type == 'caster_only':
        chat_list_filtered = [c for c in chat_list if c['speaker'] == 'cast']
    elif data_type == 'commentator_only':
        chat_list_filtered = [c for c in chat_list if c['speaker'] == 'comment']
    
    if len(chat_list_filtered) == 0:
        return False
    
    content = '### Commentary content\n'
    for chat in chat_list_filtered:
        speaker = 'caster' if chat['speaker'] == 'cast' else 'commentator'
        content += f"{speaker} : {chat['text']}\n"
    content += '\n\n### Resonse json\n'
    return content


def get_init_prompt(promt_path, game_data):
    with open(promt_path, 'r', encoding='utf-8') as file:
        init_prompt = file.read()
    home_team_players = game_data['home_lineups'].split(', ') + game_data['home_sub'].split(',')
    home_team_players = [item.split('. ')[1].strip() for item in home_team_players]
    away_team_players = game_data['away_lineups'].split(', ') + game_data['away_sub'].split(',')
    away_team_players = [item.split('.')[1].strip() for item in away_team_players]
    init_prompt = init_prompt.replace('{home_team_name}',game_data['home_team_name'])
    init_prompt = init_prompt.replace('{away_team_name}',game_data['away_team_name'])
    init_prompt = init_prompt.replace('{home_team_players}',','.join(home_team_players))
    init_prompt = init_prompt.replace('{away_team_players}',','.join(away_team_players))
    
    return init_prompt


def request_gemma(msg):
    urls = "your_gemma_endpoint_urls"
    data = {'msg' : msg,
            "repetition_penalty": 1,
            "stream": False,
            "temperature": 0.5,
            "top_p": 0.3
            }
    res = requests.post(url=urls, json=data)
    print(res.json())
    return res.json()['item']



def extract_json_to_dict(raw_str):
    start = raw_str.find('{')
    end = raw_str.rfind('}') + 1
    json_str = raw_str[start:end].replace("None", "null").replace("True", "true").replace("False", "false")
    data = json.loads(json_str)
    
    return data

def msg_to_string(chat_list, model):
    prompt = ""
    if model == 'llama':
        for msg in chat_list:
            if msg['role'] == 'user':
                prompt += "<|start_header_id|>user<|end_header_id|>"
                prompt += msg['content'] + "<|eot_id|>"
            elif msg['role'] == 'model':
                prompt += "<|start_header_id|>assistant<|end_header_id|>"
                prompt += msg['content'] + "<|eot_id|>"
    else : 
        return None
    return prompt 