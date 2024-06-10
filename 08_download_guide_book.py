import requests
import json
import os
from dotenv import dotenv_values

def download_guide_book(rewrite):
    current_course_filename = './stuff/guidebooks/currentCourse.json'
    with open(current_course_filename, 'r', encoding='utf-8') as current_course_file:
        course = json.load(current_course_file)
        
    for phaseIndex in range(len(course['currentCourse']['pathSectioned'])):
        phase = course['currentCourse']['pathSectioned'][phaseIndex]
        for partIndex in range(len(phase['units'])):
            part = phase['units'][partIndex]
            if 'guidebook' not in part or part['guidebook'] is None:
                continue
            if 'url' not in part['guidebook'] or part['guidebook']['url'] is None:
                continue

            unitIndex = part['unitIndex']
            guide_book_url = part['guidebook']['url']
            guide_book_path = f"stuff/guidebooks/phase-{phaseIndex+1:02d}"
            guide_book_filename = f"{guide_book_path}/part-{partIndex+1:02d}_guidebook-{unitIndex+1:03d}.json"

            if os.path.exists(guide_book_filename):
                if rewrite:
                    os.remove(guide_book_filename)
                else:
                    print(f"{guide_book_filename} exists")
                    continue
            os.makedirs(guide_book_path, exist_ok=True)

            response = requests.get(guide_book_url)
            if response.status_code == 200:
                data = response.json()
                with open(guide_book_filename, 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"download '{guide_book_filename}' ...")
    
def main():
    download_guide_book(False)

env_variables = dotenv_values(".env")

if __name__ == '__main__':
    main()    
