import json
import os
import pandas as pd
import urllib.request


def download_static_files(transcription, stories_path, rewrite):
    print(f"download {transcription['header']['title']} - {transcription['header']['content']['text']} ...")
    download_static_file(stories_path, transcription['header']['illustrationUrl'], rewrite)
    download_static_file(stories_path, transcription['header']['content']['audioUrl'], rewrite)
    for line in transcription['lines']:
        if 'reciter' in line:
            download_static_file(stories_path, line['reciter']['avatarUrl'], rewrite)
        download_static_file(stories_path, line['content']['audioUrl'], rewrite)


def download_static_file(stories_path, url, rewrite):
    target_filename = get_static_filename(stories_path, url)
    if os.path.exists(target_filename):
        if rewrite:
            os.remove(target_filename)
        else:
            print(f"{target_filename} exists")
            return
    print(f"{url}") 
    urllib.request.urlretrieve(url, target_filename)


def get_static_filename(stories_dir, url):
    filename = os.path.basename(url)
    if '/image/' in url:
        target_filename = f"{stories_dir}/../static/image/{filename}"
    elif '/audio/' in url:
        target_filename = f"{stories_dir}/../static/audio/{filename}"
    else:
        target_filename = f"{stories_dir}/../static/{filename}"
    return target_filename  


def main():
    stories_path = './stuff/stories'
    storie_dir_names = [name for name in os.listdir(stories_path) if os.path.isdir(f"{stories_path}/{name}")]
    for i in range(len(storie_dir_names)):
        storie_dir_name = storie_dir_names[i]
        # if 'en-zh-a-date_' not in storie_dir_name:
        #     continue
        transcription_filename = os.path.join(stories_path, storie_dir_name, 'transcription.json')
        with open(transcription_filename, 'r', encoding='utf-8') as story_file:
            transcription = json.load(story_file)
        download_static_files(transcription, stories_path, False)
        print(f"progress: {(i + 1.0) / len(storie_dir_names):.2%}")
        

if __name__ == '__main__':
    main()
