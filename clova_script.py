# test for clova script
import requests
import json
import csv
import numpy as np
import pandas as pd
import re

class ClovaSpeechClient:
    # Clova Speech invoke URL
    invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/5762/d08a1cb087732697aa64e03378caa3cd91767a3643c7a050d5d3db8a91abea35'
    # Clova Speech secret key
    secret = 'acf14278d2a74e22a3074cfe9187c9fa'

    def req_url(self, url, completion, callback=None, userdata=None, forbiddens=None, boostings=None, wordAlignment=True, fullText=True, diarization=None):
        request_body = {
            'url': url,
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        return requests.post(headers=headers,
                             url=self.invoke_url + '/recognizer/url',
                             data=json.dumps(request_body).encode('UTF-8'))

    def req_object_storage(self, data_key, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                           wordAlignment=True, fullText=True, diarization=None):
        request_body = {
            'dataKey': data_key,
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        return requests.post(headers=headers,
                             url=self.invoke_url + '/recognizer/object-storage',
                             data=json.dumps(request_body).encode('UTF-8'))

    def req_upload(self, file, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                   wordAlignment=True, fullText=True, diarization=None):
        request_body = {
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': {
                "enable": True,
                "speakerCountMin": 1,
                "speakerCountMax": 2,
            },
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        print(json.dumps(request_body, ensure_ascii=False).encode('UTF-8'))
        files = {
            'media': open(file, 'rb'),
            'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
        }
        response = requests.post(headers=headers, url=self.invoke_url + '/recognizer/upload', files=files)
        return response

def extract_filename(filepath):
    # 파일명만 추출
    filename = filepath.split('/')[-1].split('.mp3')[0]

    # 영어 단어만 추출
    english_words = re.findall(r'\b[A-Za-z]+\b', filename)
    
    # 괄호 안의 내용 추출
    date_info = re.search(r'\(([^)]+)\)', filename).group(1)
    
    # 영어와 숫자로 이루어진 패턴 (예: R1) 추출
    round_info = re.search(r'([A-Za-z]+\d+)', filename).group(1)
    
    # 특정 위치의 단어들, 괄호 안의 내용, 그리고 영어와 숫자로 이루어진 정보를 사용하여 결과 문자열 생성
    return f"{round_info} {english_words[1]} vs {english_words[3]} ({date_info})"

if __name__ == '__main__':
    # res = ClovaSpeechClient().req_url(url='http://example.com/media.mp3', completion='sync')
    # res = ClovaSpeechClient().req_object_storage(data_key='data/media.mp3', completion='sync')
    # file_name = '/Users/min/Documents/GitHub/DST/YouTubeDownloader/[하나원큐 K리그1] R1 전북 vs 서울 하이라이트 _ Jeonbuk vs Seoul Highlights (21.02.27) [4677582449059132101].mp3'
    file_name = '/Users/min/Documents/GitHub/DST/YouTubeDownloader/[2023 K리그1] 29R 대전 vs 수원FC 풀 하이라이트 [-2497952770210013757].mp3'
    res = ClovaSpeechClient().req_upload(file=file_name, completion='sync')
    result = res.json()

    # Extract speaker-separated text from result
    segments = result.get('segments', [])
    speakers_separated_texts = []

    for segment in segments:
        speaker_label = segment['speaker']['label']
        text = segment['text']
        speakers_separated_texts.append({'speaker': speaker_label, 'text': text})

    # print speaker-segmented results
    for speaker_separated_text in speakers_separated_texts:
        speaker_label = speaker_separated_text['speaker']
        text = speaker_separated_text['text']
        print(f'Speaker {speaker_label}: {text}')

    # Convert list of dicts to DataFrame
    df = pd.DataFrame(speakers_separated_texts)

    # Save DataFrame to csv
    # ex) R29_Seoul_Suwon_(220904).csv
    # csv_name = file_name.split('/')[-1].split('.')[0] + '.csv'
    # csv_name = extract_filename(file_name) + '.csv'
    csv_name = 'R29_대전_수원.csv'
    
    # columns = ['time_stamp', 'speaker', 'text']
    # make time_stamp column
    time_stamp = []
    for i in range(len(df)):
        time_stamp.append('')
    df['time_stamp'] = time_stamp
    # reorder columns
    columns = ['time_stamp', 'speaker', 'text']
    df = df[columns]
    df.to_csv(f'/Users/min/Documents/GitHub/DST/YouTubeDownloader/{csv_name}', index=False, encoding='utf-8-sig')

