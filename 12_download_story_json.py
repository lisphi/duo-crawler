import requests
import os
import json
import time
from dotenv import dotenv_values


def download_story(story_index, story_id, title, rewrite):
    story_path =f'stuff/stories/{story_index+1:04d}_{story_id}_{title}'
    story_filename = f'{story_path}/story.json'
    if os.path.exists(story_filename):
        if rewrite:
            os.remove(story_filename)
        else:
            print(f"{story_filename} exists")
            return

    print(f"download {story_filename} ...")
    story_url_template = """https://stories.duolingo.com/api2/stories/{}?crowns=495&debugShowAllChallenges=false&illustrationFormat=svg&isDesktop=true&isLegendaryMode=false&masterVersion=false&supportedElements=ARRANGE,CHALLENGE_PROMPT,DUO_POPUP,FREEFORM_WRITING,FREEFORM_WRITING_EXAMPLE_RESPONSE,FREEFORM_WRITING_PROMPT,HEADER,HINT_ONBOARDING,LINE,MATCH,MULTIPLE_CHOICE,POINT_TO_PHRASE,SECTION_HEADER,SELECT_PHRASE,SENDER_RECEIVER,SUBHEADING,TYPE_TEXT&type=story&_={}"""
    story_url = story_url_template.format(story_id, int(time.time()*1000))
    headers = {
        'Accept': 'application/json; charset=UTF-8',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Authorization': env_variables.get('Authorization'),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    response = requests.get(story_url, headers=headers)
    if response.status_code == 200:
        os.makedirs(story_path, exist_ok=True)
        data = response.json()
        with open(story_filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

def main():
    hub_stories_filename = 'stuff/stories/practiceHubStories_2024_0609.json'
    with open(hub_stories_filename, 'r', encoding='utf-8') as file:
        practiceHubStories = json.load(file)
    for i in range(len(practiceHubStories['stories'])):
        story_stub = practiceHubStories['stories'][i]
        story_id = story_stub['id']
        title = story_stub['title']
        download_story(i, story_id, title, False)
        # time.sleep(2)

env_variables = dotenv_values(".env")

if __name__ == '__main__':
    main()
