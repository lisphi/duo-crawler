import json
import os

def generate(rewrite):
    characters_filename = 'stuff/stories/characters.json'
    if os.path.exists(characters_filename):
        if rewrite:
            os.remove(characters_filename)
        else:
            print(f"{characters_filename} exists")
            return

    stories_dir = 'stuff/stories'
    storie_dirs = [name for name in os.listdir(stories_dir) if os.path.isdir(os.path.join(stories_dir, name))]
    character_dict = {}
    for dir in storie_dirs:
        story_filename = os.path.join(stories_dir, dir, 'story.json')
        with open(story_filename, 'r', encoding='utf-8') as file:
            story = json.load(file)
            header = story['elements'][0]
            title = f"{header['learningLanguageTitleContent']['text']} | {header['title']}"

            for element in story['elements']:
                if element['type'] == 'LINE':
                    line = element['line']
                    if line['type'] == 'CHARACTER':
                        characterId = line['characterId']
                        avatarUrl = line['avatarUrl']
                        characterName = line['characterNameMap']['en']
                        if characterId not in character_dict:
                            character_dict[characterId] = { 'characterId': characterId, 'characterName': characterName, 'avatarUrl': avatarUrl, 'stories': [title] }
                        else:
                            stories = character_dict[characterId]['stories']
                            if title not in stories:
                                stories.append(title)

    with open(characters_filename, 'w', encoding='utf-8') as file:
        json.dump(dict(sorted(character_dict.items(), key=lambda x: len(x[1]['stories']), reverse=True)), file, indent=4, ensure_ascii=False)


def main():
    generate(True)

if __name__ == '__main__':
    main()