import requests
import os
import json
import time
from datetime import date
from dotenv import dotenv_values


def download_practice_hub(rewrite):
    target_filename = f"stuff/stories/practiceHubStories_{date.today().strftime('%Y_%m%d')}.json"
    if os.path.exists(target_filename):
        if rewrite:
            os.remove(target_filename)
        else:
            print(f"{target_filename} exists")
            return

    url_template = """https://stories.duolingo.com/api2/practiceHubStories?featuredStoryId=en-zh-bad-monkey&fromLanguage=zh&illustrationFormat=svg&learningLanguage=en&_={}"""
    url = url_template.format(int(time.time()*1000))
    headers = {
        'Accept': 'application/json; charset=UTF-8',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Authorization': env_variables.get('Authorization'),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        with open(target_filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)



def main():
    download_practice_hub(False)

env_variables = dotenv_values(".env")

if __name__ == '__main__':
    main()
