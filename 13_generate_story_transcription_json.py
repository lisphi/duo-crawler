import json
import os
import pandas as pd


def generate_story_transcription_json(story, stories_path, storie_dir_name, rewrite):
    target_filename = os.path.join(stories_path, storie_dir_name, 'transcription.json')
    if os.path.exists(target_filename):
        if rewrite:
            os.remove(target_filename)
        else:
            print(f"{target_filename} exists")
            return

    transcription = {
        'header': {},
        'lines': [],
    }
 
    header = story['elements'][0]
    transcription['header'] = {
        'title': header['title'],
        'illustrationUrl': header['illustrationUrl'],
        'content': {
            'text': header['learningLanguageTitleContent']['text'],
            'audioUrl': header['learningLanguageTitleContent']['audio']['url'],
        },
    }

    for element in story['elements']:
        if element['type'] == 'LINE':
            line = element['line']
            if line['type'] == 'CHARACTER':
                characterId = line['characterId']
                avatarUrl = line['avatarUrl']
                characterName = line['characterNameMap']['en']
                content_text = line['content']['text']
                content_audio_url = line['content']['audio']['url']
                transcription['lines'].append({
                        'type': 'CHARACTER',
                        'reciterName': characterName,
                        'reciter': {
                            "id": characterId,
                            "name": characterName,
                            "avatarUrl": avatarUrl
                        },
                        'content': {
                            'text': content_text,
                            'audioUrl': content_audio_url
                        }
                    })
            elif line['type'] == 'PROSE':
                content_text = line['content']['text']
                content_audio_url = line['content']['audio']['url']
                transcription['lines'].append({
                        'type': 'PROSE',
                        'reciterName': '',
                        'content': {
                            'text': content_text,
                            'audioUrl': content_audio_url
                        }
                    })
    
    with open(target_filename, 'w', encoding='utf-8') as file:
        json.dump(transcription, file, indent=4, ensure_ascii=False)


def main():
    stories_path = './stuff/stories'
    storie_dir_names = [name for name in os.listdir(stories_path) if os.path.isdir(f"{stories_path}/{name}")]
    for i in range(len(storie_dir_names)):
        storie_dir_name = storie_dir_names[i]
        # if 'en-zh-a-date_' not in storie_dir_name:
        #     continue
        story_filename = os.path.join(stories_path, storie_dir_name, 'story.json')
        with open(story_filename, 'r', encoding='utf-8') as story_file:
            story = json.load(story_file)
        generate_story_transcription_json(story, stories_path, storie_dir_name, False)
        print(f"progress: {(i + 1.0) / len(storie_dir_names):.2%}")
        

if __name__ == '__main__':
    main()
