import copy
from utils import *
import argparse
import json
from openai import OpenAI 
from tqdm import tqdm
GPT_API_KEY = "PUT_YOUR_API_KEY"


def inference(data, args, model_name="gemma-9b-it"):
    
    for game in tqdm(data, desc="Game loop"):
        init_prompt = get_init_prompt(args.prompt_file_path, game['meta'])
        response = {}
        total_chat = []
        
        for game_time, chat_list in tqdm(game['commentary'].items(), desc="Time loop", leave=False):
            content = generate_content(chat_list,args.data_type)
            if not content:
                continue
            total_chat.append({'role': 'user', 'content':content})
            is_truncated, input_chat = truncate_chat(copy.deepcopy(total_chat))
            if is_truncated: # Due to the token limit, truncate the chat list to under 5000 characters.
                input_chat[0]['content'] = "\nPlease note that the previous conversation content has been omitted due to the input length limit.\n\n" + input_chat[0]['content']
            
            input_chat[0]['content'] = init_prompt + input_chat[0]['content']
            print("\n\n-----------------------INPUT Prompt---------------------\n\n")
            for chat in input_chat:
                print(f"------------{chat['role']}------------------")
                print(chat['content'])
        
            if model_name =="gemma-9b-it":
                res = request_gemma(msg=input_chat)
                print(res)
                result = extract_json_to_dict(res)

            elif model_name == "llama":
                llama_endpoint = 'your_llama_endpoint_urls'
                headers = {'Content-Type': 'application/json'}
                res = requests.post(llama_endpoint, headers=headers, data=json.dumps([input_chat]))
                result = extract_json_to_dict(res.text.replace("'",'"'))
                print(result)

            elif "gpt" in model_name:
                client = OpenAI(api_key="YOUR_API_KEY")
                res = client.chat.completions.create(
                    model = model_name,
                    messages = input_chat
                )
                res = res.choices[0].message.content
                result = extract_json_to_dict(res)
                if 'slot' in result : # 삭제 예정
                    result = result['slot']
                
            else : 
                pass
            
            response[game_time] = result

            if 'gpt' in model_name:
                total_chat.append({'role' : 'assistant', 'content' : res})
            else :
                total_chat.append({'role' : 'model', 'content' : res})

        game['response'] = response
    
        with open(args.save_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt_file_path', type=str)
    parser.add_argument('--data_file_path', type=str)
    parser.add_argument('--model', type=str)
    parser.add_argument('--save_path', type=str)
    parser.add_argument('--data_type', type=str)

    args = parser.parse_args()

    with open(args.data_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    

    inference(data, args, args.model)

