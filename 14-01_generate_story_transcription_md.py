import json
import os
import pandas as pd


def generate_story_transcription_md(transcription, stories_path, storie_dir_name, rewrite):
    filename = f"{storie_dir_name[:4]}_{storie_dir_name[11:].split('_')[0]}.md"
    target_filename = os.path.join(stories_path, storie_dir_name, filename)
    if os.path.exists(target_filename):
        if rewrite:
            os.remove(target_filename)
        else:
            print(f"{target_filename} exists")
            return
    with open(target_filename, "w", encoding='utf-8') as file:
        # story title
        file.write(f"## {storie_dir_name[:4]} · {transcription['header']['content']['text']} · {transcription['header']['title']}\n")
        # table 
        # table header
        file.write(f"| {storie_dir_name[:4]} | {transcription['header']['content']['text']} · {transcription['header']['title']} |\n")
        file.write(f"| --------: | :------- |\n")
        # table rows
        for line in transcription['lines']:
            decorated_reciter_name = line['reciterName']
            if decorated_reciter_name != '':
                decorated_reciter_name = f"**{decorated_reciter_name}**"
            file.write(f"| {decorated_reciter_name} | {line['content']['text'].replace('\n', '<br/>')} |\n")

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
        generate_story_transcription_md(transcription, stories_path, storie_dir_name, False)
        print(f"progress: {(i + 1.0) / len(storie_dir_names):.2%}")
        

if __name__ == '__main__':
    main()


