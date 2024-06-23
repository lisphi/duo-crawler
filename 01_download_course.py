import requests
import json
import os
import time
import pandas as pd
import urllib.request
from pydub import AudioSegment
import re
from dotenv import dotenv_values



def download_guidebook(phase_index, part_index, part, rewrite):
    if 'guidebook' not in part or part['guidebook'] is None:
        return
    if 'url' not in part['guidebook'] or part['guidebook']['url'] is None:
        return
    unit_index = part['unitIndex']
    guidebook_url = part['guidebook']['url']
    if guidebook_url is None:
        return
    guidebook_name = re.sub(r"[/'\s]", '-', part['teachingObjective']) # replacing blank or single-quoted characters with underscores
    
    guidebook_path = f"stuff/course{user_lang}/guidebook/phase-{phase_index+1:02d}"
    guidebook_filename = f"{guidebook_path}/{phase_index+1:02d}-{part_index+1:02d}_{guidebook_name}.json"

    if os.path.exists(guidebook_filename):
        if rewrite:
            os.remove(guidebook_filename)
        else:
            print(f"{guidebook_filename} exists")
            return
    os.makedirs(guidebook_path, exist_ok=True)

    response =  get_with_retries(guidebook_url)
    if response.status_code == 200:
        data = response.json()
        with open(guidebook_filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"200 '{guidebook_filename}'")
    else:
        print(f"{response.status_code} '{guidebook_filename}'")


def download_story(phase_index, part_index, part, story_id_set, rewrite):
    unit_index = part['unitIndex']
    for level_index in range(len(part['levels'])):
        level = part['levels'][level_index]
        if level['type'] != 'story':
            continue
        story_id = level['pathLevelClientData']['storyId']
        if story_id in story_id_set:
            continue
        story_id_set.add(story_id)
        story_path = f"stuff/course{user_lang}/story"
        story_filename = f"{story_path}/{phase_index+1:02d}-{part_index+1:02d}_{story_id[6:]}.json"
        story_url_template = """https://stories.duolingo.com/api2/stories/{}?crowns=495&debugShowAllChallenges=false&illustrationFormat=svg&isDesktop=true&isLegendaryMode=false&masterVersion=false&supportedElements=ARRANGE,CHALLENGE_PROMPT,DUO_POPUP,FREEFORM_WRITING,FREEFORM_WRITING_EXAMPLE_RESPONSE,FREEFORM_WRITING_PROMPT,HEADER,HINT_ONBOARDING,LINE,MATCH,MULTIPLE_CHOICE,POINT_TO_PHRASE,SECTION_HEADER,SELECT_PHRASE,SENDER_RECEIVER,SUBHEADING,TYPE_TEXT&type=story&_={}"""
        story_url = story_url_template.format(story_id, int(time.time()*1000))

        if os.path.exists(story_filename):
            if rewrite:
                os.remove(story_filename)
            else:
                print(f"{story_filename} exists")
                return
        os.makedirs(story_path, exist_ok=True)

        headers = {
            'Accept': 'application/json; charset=UTF-8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Authorization': env_variables.get('Authorization'),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        response = get_with_retries(story_url, headers)
        if response.status_code == 200:
            data = response.json()
            with open(story_filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"200 '{story_filename}'")
        else:
            print(f"{response.status_code} '{story_filename}'")
        time.sleep(0.2)


def get_with_retries(url, headers = None, max_retries = 3):
    retries = 0
    while retries < max_retries:
        response = requests.get(url, headers=headers)
        if 500 <= response.status_code < 600:
            retries += 1
            print(f"{response.status_code} '{url}' retrying {retries}/{max_retries}...")
            time.sleep(2 * retries)
        else:
            return response
    return response


def download_courses(rewrite):
    current_course_filename = f"./stuff/course{user_lang}/currentCourse.json"
    with open(current_course_filename, 'r', encoding='utf-8') as current_course_file:
        course = json.load(current_course_file)
        
    story_id_set = set()
    for phase_index in range(len(course['currentCourse']['pathSectioned'])):
        phase = course['currentCourse']['pathSectioned'][phase_index]
        for part_index in range(len(phase['units'])):
            part = phase['units'][part_index]
            download_guidebook(phase_index, part_index, part, rewrite)
            # download_story(phase_index, part_index, part, story_id_set, rewrite)




def download_story_static_file(story, rewrite):
    for element in story['elements']:
        if element['type'] == 'HEADER':
            download_static_file(element['illustrationUrl'], rewrite)
            download_static_file(element['learningLanguageTitleContent']['audio']['url'], rewrite)
        if element['type'] == 'LINE':
            download_static_file(element['line']['content']['audio']['url'], rewrite)
            if 'avatarUrl' in element['line']:
                download_static_file(element['line']['avatarUrl'], rewrite)


def download_static_file(url, rewrite):
    target_filename = get_static_filename(url)
    if os.path.exists(target_filename):
        if rewrite:
            os.remove(target_filename)
        else:
            print(f"file exists: '{target_filename}'")
            return
    urllib.request.urlretrieve(url, target_filename)
    print(f"downloaded '{target_filename}'") 


def get_static_filename(url):
    filename = os.path.basename(url)
    if '/image/' in url:
        target_filename = f"./stuff/static/image/{filename}"
    elif '/audio/' in url:
        target_filename = f"./stuff/static/audio/{filename}"
    else:
        target_filename = f"./stuff/static/{filename}"
    return target_filename  


def download_story_static_files(rewrite):
    story_path = f"./stuff/course{user_lang}/story"
    filenames = [filename for filename in os.listdir(story_path) if filename.endswith('.json')]
    for i in range(len(filenames)):
        story_filename = f"{story_path}/{filenames[i]}" 
        with open(story_filename, 'r', encoding='utf-8') as story_file:
            story = json.load(story_file)
        print(f"downloading static files of '{story_filename}' ...")
        download_story_static_file(story, rewrite)
        print(f"downloaded static files of '{story_filename}' {(i + 1.0) / len(filenames):.2%}")
        



def generate_story_mp3_file(story_filename, rewrite):
    target_mp3_filename = f"{story_filename[:-5]}.mp3"
    target_lrc_filename = f"{story_filename[:-5]}.lrc"

    if os.path.exists(target_mp3_filename):
        if rewrite:
            os.remove(target_mp3_filename)
        else:
            print(f"{target_mp3_filename} exists")
            return

    if os.path.exists(target_lrc_filename) and rewrite:
        os.remove(target_lrc_filename)

    with open(story_filename, 'r', encoding='utf-8') as story_file:
        story = json.load(story_file)

    merged = AudioSegment.empty()
    lyrics = []
    total_duration_ms = 0
    for element in story['elements']:
        if element['type'] == 'HEADER':
            title = element['learningLanguageTitleContent']['text']
            audio_url = element['learningLanguageTitleContent']['audio']['url']
            lyrics.append(f"[00:00.00]{title}")
            audio_filename = get_static_filename(audio_url)
            audio = AudioSegment.from_mp3(audio_filename)
            merged += audio
            total_duration_ms += len(audio)
            pause_audio = AudioSegment.silent(1000) 
            merged += pause_audio
            total_duration_ms += 1000
        if element['type'] == 'LINE':
            if 'characterNameMap' in element['line']:
                reciter_name = f"({element['line']['characterNameMap']['en']})" 
            else:
                reciter_name = ''
            if element['line']['type'] == 'SECTION_HEADER':
                reciter_name = f"(SECTION)"
                silent_duration_ms = 600
            else:
                silent_duration_ms = 300
            audio_url = element['line']['content']['audio']['url']
            text = element['line']['content']['text']
            lyrics.append(f"[{format_duration(total_duration_ms)}]{reciter_name}{text}")
            audio_filename = get_static_filename(audio_url)
            audio = AudioSegment.from_mp3(audio_filename)
            merged += audio
            total_duration_ms += len(audio)
            pause_audio = AudioSegment.silent(silent_duration_ms) 
            merged += pause_audio
            total_duration_ms += silent_duration_ms
    
    merged += AudioSegment.silent(2700)
    merged.export(target_mp3_filename, format="mp3")

    with open(target_lrc_filename, 'w', encoding='utf-8') as outfile_lrc:
        for lyric in lyrics:
            outfile_lrc.write(lyric)
            outfile_lrc.write('\n')


def format_duration(duration_ms):
    total_seconds = duration_ms // 1000
    milliseconds = duration_ms % 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    milliseconds = milliseconds / 10
    return f"{minutes:02}:{seconds:02}.{milliseconds:02.0f}"       


def generate_story_mp3_files(rewrite):
    story_path = f"./stuff/course{user_lang}/story"
    filenames = [filename for filename in os.listdir(story_path) if filename.endswith('.json')]
    for i in range(len(filenames)):
        story_filename = f"{story_path}/{filenames[i]}" 
        print(f"generating mp3 file of '{story_filename}' ...")
        generate_story_mp3_file(story_filename, rewrite)
        print(f"generatied mp3 file of '{story_filename}' {(i + 1.0) / len(filenames):.2%}")




def main():
    print('start ...')
    download_courses(False)
    # download_story_static_files(False)
    # generate_story_mp3_files(False)




env_variables = dotenv_values(".env")
# user_lang = ""
user_lang = "-zh"
# user_lang = "-es"
# user_lang = "-ja"

if __name__ == '__main__':
    main()    
