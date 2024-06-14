
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
    target_mp3_filename = f"{stories_path}/{storie_dir_name}/{storie_dir_name[:4]}_{storie_dir_name[11:].split('_')[0]}.mp3"
    target_lrc_filename = f"{stories_path}/{storie_dir_name}/{storie_dir_name[:4]}_{storie_dir_name[11:].split('_')[0]}.lrc"

    if os.path.exists(target_mp3_filename):
        if rewrite:
            os.remove(target_mp3_filename)
        else:
            print(f"{target_mp3_filename} exists")

    if os.path.exists(target_lrc_filename) and rewrite:
        os.remove(target_lrc_filename)            

    lyrics = []
    lyrics.append(f"[00:00.00]{transcription['header']['content']['text']} - {transcription['header']['title']}")

    merged = AudioSegment.empty()
    header_audio_filename = get_static_filename(stories_path, transcription['header']['content']['audioUrl'])
    header_audio = AudioSegment.from_mp3(header_audio_filename)
    merged += header_audio
    total_duration = len(header_audio)


    for i in range(len(transcription['lines'])):
        line = transcription['lines'][i]

        if i == 0:
            pause_duration_ms = 1000
        else:
            pause_duration_ms = 300
        pause_audio = AudioSegment.silent(pause_duration_ms) 
        merged += pause_audio
        total_duration += pause_duration_ms

        lyrics.append(f"[{format_duration(total_duration)}]{line['content']['text']}")

        line_audio_filename = get_static_filename(stories_path, line['content']['audioUrl'])
        line_audio = AudioSegment.from_mp3(line_audio_filename)
        merged += line_audio
        total_duration += len(line_audio)

    merged += AudioSegment.silent(3000)
    merged.export(target_mp3_filename, format="mp3")

    with open(target_lrc_filename, 'w', encoding='utf-8') as outfile_lrc:
        for lyric in lyrics:
            outfile_lrc.write(lyric)
            outfile_lrc.write('\n')


def format_duration(duration):
    total_seconds = duration // 1000
    milliseconds = duration % 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    milliseconds = milliseconds / 10
    return f"{minutes:02}:{seconds:02}.{milliseconds:02.0f}"       


def main():
    stories_path = './stuff/stories'
    storie_dir_names = [name for name in os.listdir(stories_path) if os.path.isdir(f"{stories_path}/{name}")]
    for i in range(len(storie_dir_names)):
        storie_dir_name = storie_dir_names[i]
        transcription_filename = os.path.join(stories_path, storie_dir_name, 'transcription.json')
        with open(transcription_filename, 'r', encoding='utf-8') as story_file:
            transcription = json.load(story_file)
        generate_story_audio_mp3(transcription, stories_path, storie_dir_name, True)
        print(f"progress: {(i + 1.0) / len(storie_dir_names):.2%}")
        

if __name__ == '__main__':
    main()    