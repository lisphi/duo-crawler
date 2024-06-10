
import json
import os
from pydub import AudioSegment


def get_static_filename(stories_path, url):
    filename = os.path.basename(url)
    if '/image/' in url:
        target_filename = f"{stories_path}/../static/image/{filename}"
    elif '/audio/' in url:
        target_filename = f"{stories_path}/../static/audio/{filename}"
    else:
        target_filename = f"{stories_path}/../static/{filename}"
    return target_filename  


def generate_story_audio_mp3(transcription, stories_path, storie_dir_name, rewrite):
    filename = f"{storie_dir_name[:4]}_{storie_dir_name[11:].split('_')[0]}.mp3"
    target_filename = os.path.join(stories_path, storie_dir_name, filename)
    if os.path.exists(target_filename):
        if rewrite:
            os.remove(target_filename)
        else:
            print(f"{target_filename} exists")
            return
        
    merged = AudioSegment.empty()
    header_audio_filename = get_static_filename(stories_path, transcription['header']['content']['audioUrl'])
    header_audio = AudioSegment.from_mp3(header_audio_filename)
    merged += header_audio

    pause_duration_ms = 300
    pause_audio = AudioSegment.silent(pause_duration_ms) 
    merged += pause_audio

    for i in range(len(transcription['lines'])):
        if i == 0:
            pause_duration_ms = 500
        else:
            pause_duration_ms = 300
        pause_audio = AudioSegment.silent(pause_duration_ms) 
        merged += pause_audio

        line = transcription['lines'][i]
        line_audio_filename = get_static_filename(stories_path, line['content']['audioUrl'])
        line_audio = AudioSegment.from_mp3(line_audio_filename)
        merged += line_audio

    merged.export(target_filename, format="mp3")  


def main():
    stories_path = './stuff/stories'
    storie_dir_names = [name for name in os.listdir(stories_path) if os.path.isdir(f"{stories_path}/{name}")]
    for i in range(len(storie_dir_names)):
        storie_dir_name = storie_dir_names[i]
        # if 'the-perfect-girlfriend' not in storie_dir_name:
        #     continue
        transcription_filename = os.path.join(stories_path, storie_dir_name, 'transcription.json')
        with open(transcription_filename, 'r', encoding='utf-8') as story_file:
            transcription = json.load(story_file)
        generate_story_audio_mp3(transcription, stories_path, storie_dir_name, False)
        print(f"progress: {(i + 1.0) / len(storie_dir_names):.2%}")
        

if __name__ == '__main__':
    main()    