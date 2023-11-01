from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd
import re

def convert_event_time(time, is_second_half=False):
    # 문자에서 숫자만 추출
    time = re.sub(r"[^0-9]", "", time)
    time_val = int(time)

    # 후반 시작 이후라면 45를 더함
    if is_second_half:
        time_val += 45
        if time_val > 90:
            added_time = time_val - 90
            return f"90+{added_time}"
        else:
            return f"{time_val}"
    else:
        if time_val > 45 and time_val <= 90:
            added_time = time_val - 45
            return f"45+{added_time}"
        else:
            return f"{time_val}"
        
def extract_date(driver):
    element = driver.find_element(By.XPATH, '//div[@class="sort-box"]')
    date_pattern = re.compile(r"(\d{4}\.\d{2}\.\d{2})")
    match = date_pattern.search(element.text)
    return match.group(1) if match else None

def extract_team_name(driver, position):
    team_name_element = driver.find_element(By.CSS_SELECTOR, f".score-box .team-box:nth-child({position})").text.split("\n")[0].strip()
    return team_name_element.replace("Home Team:", "").replace("Away Team:", "").strip()

def extract_event_data(driver):
    timeline = driver.find_element(By.CSS_SELECTOR, "ul#timeline")
    is_second_half = False
    events = []

    for li in timeline.find_elements(By.TAG_NAME, 'li'):
        event_data = {}
        event_data['team_type'] = "home" if "home" in li.get_attribute("class") else "away"
        
        context_div = li.find_element(By.CSS_SELECTOR, 'div.context')
        event_parts = context_div.text.split("\n")
        event_data['event_name'] = event_parts[0]

        # Convert event time
        time_element = li.find_element(By.CSS_SELECTOR, 'div.min span')
        event_time = time_element.text.strip() if time_element else None
        if event_data['event_name'] == "후반시작":
            is_second_half = True
        event_data['event_time'] = convert_event_time(time=event_time, is_second_half=is_second_half)

        # Event details
        if len(event_parts) > 1:
            details = event_parts[1].split(',')
            event_data['team_name'] = details[0].split()[0] if " " in details[0] else None
            event_data['event_detail'] = details[1].strip() if len(details) > 1 else None
        else:
            event_data['team_name'] = None
            event_data['event_detail'] = None
        
        # Handling substitutions
        if "교체" in event_data['event_name']:
            in_player = None
            out_player = None
            for part in event_parts:
                if "In" in part:
                    in_player = part.split("In")[-1].strip()
                if "Out" in part:
                    out_player = part.split("Out")[-1].strip()
            event_data['in_player'] = in_player
            event_data['out_player'] = out_player

        events.append(event_data)
    
    return events

def extract_lineups(driver):
    positions = ['gk', 'df', 'mf', 'fw', 'bench']
    home_lineups = {'starting': [], 'substitutes': []}
    away_lineups = {'starting': [], 'substitutes': []}

    for position in positions:
        players = driver.find_elements(By.XPATH, f'//ul[@class="{position}"]/li')
        for player in players:
            # 홈 팀 선수 정보 추출
            try:
                home_name = player.find_element(By.XPATH, './/div[contains(@class, "home-lineup")]/span[@class="name"]').text
                if position != 'bench':
                    home_lineups['starting'].append(home_name)
                else:
                    home_lineups['substitutes'].append(home_name)
            except:
                pass

            # 원정 팀 선수 정보 추출
            try:
                away_name = player.find_element(By.XPATH, './/div[contains(@class, "away-lineup")]/span[@class="name"]').text
                if position != 'bench':
                    away_lineups['starting'].append(away_name)
                else:
                    away_lineups['substitutes'].append(away_name)
            except:
                pass

    return home_lineups, away_lineups

def extract_events(driver):
    events = []
    
    # 해당 element를 찾습니다.
    timeline = driver.find_element(By.CSS_SELECTOR, "ul#timeline")
    is_second_half_bool = False

    # 각 li 태그를 순회하며 정보를 추출
    for li in timeline.find_elements(By.TAG_NAME, 'li'):
        event_data = {}
        
        # home/away 정보 확인
        event_data["team_type"] = "home" if "home" in li.get_attribute("class") else "away"
        
        context_div = li.find_element(By.CSS_SELECTOR, 'div.context')
        event_parts = context_div.text.split("\n")
        event_data["event_name"] = event_parts[0]

        # 이벤트 시간 추출
        time_element = li.find_element(By.CSS_SELECTOR, 'div.min span')
        event_time = time_element.text.strip() if time_element else None
        event_data["event_time"] = convert_event_time(time = event_time, is_second_half=is_second_half_bool)
        
        # 세부 정보 추출
        if len(event_parts) > 1:
            details = event_parts[1].split(',')
            event_data["team_name"] = details[0].split()[0] if " " in details[0] else None
            event_data["event_detail"] = details[1].strip() if len(details) > 1 else None
        else:
            event_data["team_name"] = None
            event_data["event_detail"] = None

        # 교체에 대한 처리
        if "교체" in event_data["event_name"]:
            for part in event_parts:
                if "In" in part:
                    event_data["in_player"] = part.split("In")[-1].strip()
                if "Out" in part:
                    event_data["out_player"] = part.split("Out")[-1].strip()
        else:
            event_data["in_player"] = None
            event_data["out_player"] = None
        
        events.append(event_data)

    return events

def update_csv_file(csv_path, driver):
    df = pd.read_csv(csv_path)

    for index, row in df.iterrows():
        match_url = row['match_url']
        driver.get(match_url)
        time.sleep(3)
        
        # 날짜 정보 및 홈, 어웨이팀 정보 수집...
        date = extract_date(driver)
        home_team_name = extract_team_name(driver, 1)
        away_team_name = extract_team_name(driver, 3)
        
        # 각 행에 수집된 정보 업데이트
        df.at[index, 'date'] = date
        df['home_team_name'] = df['home_team_name'].astype(str)
        df['away_team_name'] = df['away_team_name'].astype(str)
        df.at[index, 'home_team_name'] = home_team_name
        df.at[index, 'away_team_name'] = away_team_name

        highlights_data = []

        # 이벤트 데이터 추출
        events = extract_event_data(driver)
        for event in events:
            # 교체 이벤트일 경우
            if "교체" in event['event_name']:
                team_name = home_team_name if event['team_type'] == "home" else away_team_name
                highlights_data.append(f"{event['event_time']}', {event['team_type']}, {team_name}, 교체, None, In {event['in_player']} Out {event['out_player']}")
            # 그 외의 이벤트
            else:
                team_name_detail = event['team_name'] if event['team_name'] else 'None'
                event_detail_text = f"{team_name_detail} {event['event_detail']}" if event['event_detail'] else ''
                highlights_data.append(f"{event['event_time']}', {event['team_type']}, {team_name_detail}, {event['event_name']}, {event_detail_text}")

        # DataFrame에 할당
        df['highlights'] = df['highlights'].astype(str)
        df.at[index, 'highlights'] = '\n'.join(highlights_data)

        # 라인업 데이터 추출
        lineup_element = driver.find_element(By.XPATH, "//span[contains(text(), '라인업')]")
        lineup_element.click()
        time.sleep(3)

        home_lineups, away_lineups = extract_lineups(driver)

        df['home_lineups'] = df['home_lineups'].astype(str)
        df['away_lineups'] = df['away_lineups'].astype(str)
        df.at[index, 'home_lineups'] = ', '.join(home_lineups['starting']) if home_lineups['starting'] else 'None'
        df.at[index, 'away_lineups'] = ', '.join(away_lineups['starting']) if away_lineups['starting'] else 'None'

        df['home_sub'] = df['home_sub'].astype(str)
        df['away_sub'] = df['away_sub'].astype(str)
        df.at[index, 'home_sub'] = ', '.join(home_lineups['substitutes']) if home_lineups['substitutes'] else 'None'
        df.at[index, 'away_sub'] = ', '.join(away_lineups['substitutes']) if away_lineups['substitutes'] else 'None'

        # url에 값이 존재하지 않는다면 크롤링 완료로 표시
        if pd.isnull(match_url) or match_url == '' or match_url == 'None':
            print('crawling completed')
            break
    # 수정된 DataFrame을 다시 CSV 파일로 저장
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

def main():
    driver = webdriver.Chrome()
    # csv_path = r'/Users/min/Documents/GitHub/K_league/match_url/k_league_1_21.csv'
    csv_path = r'/Users/min/Documents/GitHub/K_league/match_url/k_league_test.csv'
    update_csv_file(csv_path, driver)
    driver.quit()
    
if __name__ == "__main__":
    main()
