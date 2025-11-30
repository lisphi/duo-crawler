import requests
import json
import os
import time
import urllib.request
from pydub import AudioSegment
import re
import hashlib
from itertools import groupby
from dotenv import dotenv_values


class DuoCrawler():
    def __init__(self, from_lang=None):
        if from_lang is None:
            self._native_lang = 'es'
        else:
            self._native_lang = from_lang
        env_variables = dotenv_values('.env')
        self.jwt_token = env_variables.get('jwt_token')
        self.authorization = f'Bearer {self.jwt_token}'
        self.user_id = env_variables.get('user_id')
        self.my_base_url = f'https://www.duolingo.com/2017-06-30/users/{self.user_id}'
        self.sessions_url = 'https://ios-api-2.duolingo.com/2023-05-23/sessions'


    def download_sessions(self):
        timestamp = int(time.time() * 1000)
        url = self.sessions_url
        hhmmss = time.strftime('%Y_%m%d_%H%M%S', time.localtime(timestamp / 1000))
        file_path = f'./.stuff/sessions-{self._native_lang}-{hhmmss}.json'
        response = self._request_with_retries(url)
        if response.status_code == 200:
            data = response.json()
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f'200 "{file_path}"')
        else:
            print(f'{response.status_code} "{url}"')
            return


    def download_base_info(self):
        fields = 'acquisitionSurveyReason,adsConfig,animationEnabled,betaStatus,blockedUserIds,' \
            'blockerUserIds,canUseModerationTools,classroomLeaderboardsEnabled,courses,creationDate,' \
            'currentCourseId,email,emailAnnouncement,emailAssignment,emailAssignmentComplete,' \
            'emailClassroomJoin,emailClassroomLeave,emailEditSuggested,emailEventsDigest,emailFollow,' \
            'emailPass,emailPromotion,emailResearch,emailWeeklyProgressReport,emailSchoolsAnnouncement,' \
            'emailSchoolsNewsletter,emailSchoolsProductUpdate,emailSchoolsPromotion,emailStreamPost,emailVerified,' \
            'emailWeeklyReport,enableMicrophone,enableSoundEffects,enableSpeaker,experiments%7Bminfra_web_stripe_setup_intent,' \
            'path_web_course_complete_slides,path_web_sections_overview,placeholder_experiment,spack_web_fp_upgrade_hook_v2,spack_web_ios_pf_apple_pay_btn,' \
            'web_desquintify_tap_tokens%7D,facebookId,fromLanguage,gemsConfig,globalAmbassadorStatus,' \
            'googleId,hasFacebookId,hasGoogleId,hasPlus,health,' \
            'id,inviteURL,joinedClassroomIds,lastResurrectionTimestamp,' \
            'learningLanguage,location,name,observedClassroomIds,optionalFeatures,' \
            'persistentNotifications,picture,plusDiscounts,practiceReminderSettings,' \
            'privacySettings,referralInfo,rewardBundles,roles,sessionCount,' \
            'shouldPreventMonetizationForSchoolsUser,streak,streakData%7BcurrentStreak,longestStreak,previousStreak%7D,' \
            'timezone,timezoneOffset,totalXp,trackingProperties,username,' \
            'webNotificationIds,xpGains,xpGoal,zhTw,currentCourse'
        timestamp = int(time.time() * 1000)
        url = f'{self.my_base_url}?fields={fields}&_={timestamp}'
        hhmmss = time.strftime('%Y_%m%d_%H%M%S', time.localtime(timestamp / 1000))
        file_path = f'./.stuff/baseInfo-{self._native_lang}-{hhmmss}.json'
        response = self._request_with_retries(url)
        if response.status_code == 200:
            data = response.json()
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f'200 "{file_path}"')
        else:
            print(f'{response.status_code} "{url}"')
            return


    def download_courses(self, rewrite):
        current_course_filename = f"./.stuff/course-{self._native_lang}/currentCourse.json"
        with open(current_course_filename, 'r', encoding='utf-8') as current_course_file:
            course = json.load(current_course_file)
            
        story_id_set = set()
        for phase_index in range(len(course['currentCourse']['pathSectioned'])):
            phase = course['currentCourse']['pathSectioned'][phase_index]
            for part_index in range(len(phase['units'])):
                part = phase['units'][part_index]
                self._download_part(phase_index, part_index, part, rewrite)
                self._download_guidebook(phase_index, part_index, part, rewrite)
                self._download_story(phase_index, part_index, part, story_id_set, rewrite)


    def download_story_static_files(self, rewrite):
        story_root_path = f"./.stuff/course-{self._native_lang}/story"
        phase_dirs = [phase_dir for phase_dir in os.listdir(story_root_path) if os.path.isdir(f"{story_root_path}/{phase_dir}")]
        story_filenames =[]
        for phase_dir in phase_dirs:
            filenames = [filename for filename in os.listdir(f"{story_root_path}/{phase_dir}") if filename.endswith('.json')]
            story_filenames.extend([f"{story_root_path}/{phase_dir}/{filename}" for filename in filenames])
        for i in range(len(story_filenames)):
            story_filename = story_filenames[i]
            print(f"downloading static files for '{story_filename}' ...")
            self._download_story_static_file(story_filename, rewrite)
            print(f"downloaded static files for '{story_filename}' {(i + 1.0) / len(story_filenames):.2%}")


    def generate_story_mp3_files(self, rewrite):
        story_root_path = f"./.stuff/course-{self._native_lang}/story"
        phase_dirs = [phase_dir for phase_dir in os.listdir(story_root_path) if os.path.isdir(f"{story_root_path}/{phase_dir}")]
        story_filenames =[]
        for phase_dir in phase_dirs:
            filenames = [filename for filename in os.listdir(f"{story_root_path}/{phase_dir}") if filename.endswith('.json')]
            story_filenames.extend([f"{story_root_path}/{phase_dir}/{filename}" for filename in filenames])

        for i in range(len(story_filenames)):
            story_filename = story_filenames[i]
            print(f"generating mp3 file for '{story_filename}' ...")
            self._generate_story_mp3_file(story_filename, rewrite)
            print(f"generatied mp3 file for '{story_filename}' {(i + 1.0) / len(story_filenames):.2%}")


    def download_part_static_files(self, rewrite):
        part_root_path = f"./.stuff/course-{self._native_lang}/part"
        phase_dirs = [phase_dir for phase_dir in os.listdir(part_root_path) if os.path.isdir(f"{part_root_path}/{phase_dir}")]
        level_filenames =[]
        for phase_dir in phase_dirs:
            filenames = [filename for filename in os.listdir(f"{part_root_path}/{phase_dir}") if filename.endswith('.json')]
            level_filenames.extend([f"{part_root_path}/{phase_dir}/{filename}" for filename in filenames])    
        for i in range(len(level_filenames)):
            level_filename = level_filenames[i]
            print(f"downloading static files for '{level_filename}' ...")
            self._download_part_static_file(level_filename, rewrite)
            print(f"downloaded static files for '{level_filename}' {(i + 1.0) / len(level_filenames):.2%}")


    def generate_part_mp3_files(self, rewrite):
        part_root_path = f"./.stuff/course-{self._native_lang}/part"
        phase_dirs = [phase_dir for phase_dir in os.listdir(part_root_path) if os.path.isdir(f"{part_root_path}/{phase_dir}")]
        level_filenames =[]
        for phase_dir in phase_dirs:
            filenames = [filename for filename in os.listdir(f"{part_root_path}/{phase_dir}") if filename.endswith('.json')]
            level_filenames.extend([f"{part_root_path}/{phase_dir}/{filename}" for filename in filenames])
        level_filenames.sort()
        for key, value in groupby(level_filenames, lambda x : x[:-8]):
            self._generate_part_mp3_file(key, list(value), rewrite)
  

    def _download_part(self, phase_index, part_index, part, rewrite):
        if phase_index > 7:
            return
        type_map = {
            'skill-regular': 'LEXEME_SKILL_LEVEL_PRACTICE',
            'skill-grammar': 'LESSON',
            'practice-practice': 'LEXEME_PRACTICE',
            'practice-unit_practice': 'UNIT_PRACTICE'
        }
        for level_index in range(len(part['levels'])):
            level = part['levels'][level_index]
            if level['type'] in { 'story', 'chest', 'unit_review' }:
                continue
            if f"{level['type']}-{level['subtype']}" not in type_map:
                print(f"type not match: 'https://www.duolingo.com/lesson/unit/{part['unitIndex']+1}/level/{level_index+1}'")

            if 'skillIds' in level['pathLevelClientData']:
                skill_ids = level['pathLevelClientData']['skillIds']
            elif 'skillId' in level['pathLevelClientData']:
                skill_id = level['pathLevelClientData']['skillId']
                skill_ids = [skill_id]
            level_path = f"stuff/course-{self._native_lang}/part/{phase_index+1:02d}"
            level_filename = f"{level_path}/{phase_index+1:02d}-{part_index+1:02d}-{level_index+1:02d}.json"
            if os.path.exists(level_filename):
                if rewrite:
                    os.remove(level_filename)
                else:
                    print(f"{level_filename} exists")
                    continue
            os.makedirs(level_path, exist_ok=True)
            data =  {
                "challengeTypes": [
                    "assist", "characterIntro", "characterMatch", "characterPuzzle", "characterSelect", "characterTrace",
                    "characterWrite", "completeReverseTranslation", "definition", "dialogue", "extendedMatch", "extendedListenMatch",
                    "form", "freeResponse", "gapFill", "judge", "listen", "listenComplete", "listenMatch", "match", "name",
                    "listenComprehension", "listenIsolation", "listenSpeak", "listenTap", "orderTapComplete", "partialListen",
                    "partialReverseTranslate", "patternTapComplete", "radioBinary", "radioImageSelect", "radioListenMatch",
                    "radioListenRecognize", "radioSelect", "readComprehension", "reverseAssist", "sameDifferent", "select",
                    "selectPronunciation", "selectTranscription", "svgPuzzle", "syllableTap", "syllableListenTap", "speak",
                    "tapCloze", "tapClozeTable", "tapComplete", "tapCompleteTable", "tapDescribe", "translate", "transliterate",
                    "transliterationAssist", "typeCloze", "typeClozeTable", "typeComplete", "typeCompleteTable", "writeComprehension"
                ],
                "fromLanguage": f'{self._native_lang}',
                "isFinalLevel": False,
                "isV2": True,
                "juicy": True,
                "learningLanguage": "en",
                "pathExperiments": ["UNIT_VISION_BB_93"],
                "type": type_map.get(f"{level['type']}-{level['subtype']}"),
                "levelSessionIndex": 0
            }
            if level['type'] == 'practice':
                data["lexemePracticeType"] = "practice_level"
            if level['subtype'] =='grammar':
                data["isGrammarSkill"] = True
                data["showGrammarSkillSplash"] = False
                data["skillId"] = skill_id
                data["levelIndex"] = 0
            else:
                data["skillIds"] = skill_ids  

            response =  self._request_with_retries('https://www.duolingo.com/2017-06-30/sessions', None, data)
            if response.status_code == 200:
                data = response.json()
                with open(level_filename, 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
                print(f"200 '{level_filename}'")
            else:
                print(f"{response.status_code} '{level_filename}'")


    def _download_guidebook(self, phase_index, part_index, part, rewrite):
        if 'guidebook' not in part or part['guidebook'] is None:
            return
        if 'url' not in part['guidebook'] or part['guidebook']['url'] is None:
            return
        unit_index = part['unitIndex']
        guidebook_url = part['guidebook']['url']
        if guidebook_url is None:
            return
        guidebook_name = re.sub(r"[/'\s]", '-', part['teachingObjective']) # replacing blank or single-quoted characters with underscores
        
        guidebook_path = f"stuff/course-{self._native_lang}/guidebook/{phase_index+1:02d}"
        guidebook_filename = f"{guidebook_path}/{phase_index+1:02d}-{part_index+1:02d}_{guidebook_name}.json"

        if os.path.exists(guidebook_filename):
            if rewrite:
                os.remove(guidebook_filename)
            else:
                print(f"{guidebook_filename} exists")
                return
        os.makedirs(guidebook_path, exist_ok=True)

        response =  self._request_with_retries(guidebook_url, {})
        if response.status_code == 200:
            data = response.json()
            with open(guidebook_filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"200 '{guidebook_filename}'")
        else:
            print(f"{response.status_code} '{guidebook_filename}'")


    def _download_story(self, phase_index, part_index, part, story_id_set, rewrite):
        unit_index = part['unitIndex']
        for level_index in range(len(part['levels'])):
            level = part['levels'][level_index]
            if level['type'] != 'story':
                continue
            story_id = level['pathLevelClientData']['storyId']
            if story_id in story_id_set:
                continue
            story_id_set.add(story_id)
            story_path = f"stuff/course-{self._native_lang}/story/{phase_index+1:02d}"
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

            response = self._request_with_retries(story_url)
            if response.status_code == 200:
                data = response.json()
                with open(story_filename, 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
                print(f"200 '{story_filename}'")
            else:
                print(f"{response.status_code} '{story_filename}'")
            time.sleep(0.2)


    def _request_with_retries(self, url, headers = None, data = None, max_retries = 3):
        retries = 0
        the_headers = {
            'Accept': 'application/json; charset=UTF-8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Authorization': self.authorization,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        if headers:
            the_headers.update(headers)
        the_data = data

        while retries < max_retries:
            if data:
                res = requests.post(url, headers=the_headers, json=the_data)
            else:
                res = requests.get(url, headers=the_headers)
            if 500 <= res.status_code < 600:
                retries += 1
                print(f"{res.status_code} '{url}' retrying {retries}/{max_retries}...")
                time.sleep(2 * retries)
            else:
                return res
        return res


    def _download_story_static_file(self, story_filename, rewrite):
        with open(story_filename, 'r', encoding='utf-8') as story_file:
            story = json.load(story_file)

        for element in story['elements']:
            if element['type'] == 'HEADER':
                self._download_static_file(element['illustrationUrl'], rewrite)
                self._download_static_file(element['learningLanguageTitleContent']['audio']['url'], rewrite)
            if element['type'] == 'LINE':
                self._download_static_file(element['line']['content']['audio']['url'], rewrite)
                if 'avatarUrl' in element['line']:
                    self._download_static_file(element['line']['avatarUrl'], rewrite)


    def _download_static_file(self, url, rewrite):
        target_filename = self._get_static_filename(url)
        if os.path.exists(target_filename):
            if rewrite:
                os.remove(target_filename)
            else:
                print(f"file exists: '{target_filename}'")
                return
        target_path = os.path.dirname(target_filename)
        os.makedirs(target_path, exist_ok=True)
        urllib.request.urlretrieve(url, target_filename)
        print(f"downloaded '{target_filename}'") 


    def _get_static_filename(self, url):
        filename = os.path.basename(url)
        prefix_filename, _ = os.path.splitext(filename)
        mod64 = int(hashlib.sha256(prefix_filename.encode()).hexdigest(), 16) % 64
        if '/image/' in url:
            target_filename = f"./.stuff/static/image/{mod64:02d}/{filename}"
        elif '/audio/' in url:
            target_filename = f"./.stuff/static/audio/{mod64:02d}/{filename}"
        elif '/beaen/' in url:
            target_filename = f"./.stuff/static/beaen/{mod64:02d}/{filename}.mp3"
        elif '/eddyen/' in url:
            target_filename = f"./.stuff/static/eddyen/{mod64:02d}/{filename}.mp3"
        else:
            print(url)
            target_filename = f"./.stuff/static/{filename}"
        return target_filename


    def _download_part_static_file(self, level_filename, rewrite):
        with open(level_filename, 'r', encoding='utf-8') as level_file:
            level = json.load(level_file)

        for challenge in level['challenges']:
            if challenge['type'] == 'listenComprehension':
                self._download_static_file(challenge['tts'], rewrite)


    def _generate_story_mp3_file(self, story_filename, rewrite):
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
                audio_filename = self._get_static_filename(audio_url)
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
                text = element['line']['content']['text'].replace('\n', ' ')
                lyrics.append(f"[{self._format_duration(total_duration_ms)}]{reciter_name}{text}")
                audio_filename = self._get_static_filename(audio_url)
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


    def _format_duration(self, duration_ms):
        total_seconds = duration_ms // 1000
        milliseconds = duration_ms % 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        milliseconds = milliseconds / 10
        return f"{minutes:02}:{seconds:02}.{milliseconds:02.0f}"       


    def _generate_part_mp3_file(self, target_filename_no_extension, level_filenames, rewrite):
        target_mp3_filename = f"{target_filename_no_extension}.mp3"
        target_lrc_filename = f"{target_filename_no_extension}.lrc"
        if os.path.exists(target_mp3_filename):
            if rewrite:
                os.remove(target_mp3_filename)
            else:
                print(f"{target_mp3_filename} exists")
                return
        if os.path.exists(target_lrc_filename) and rewrite:
            os.remove(target_lrc_filename)
        listenComprehensions = []
        for level_filename in level_filenames:
            with open(level_filename, 'r', encoding='utf-8') as story_file:
                level = json.load(story_file)
            for challenge in level['challenges']:
                if challenge['type'] == 'listenComprehension':
                    prompt = challenge['prompt']
                    tts = challenge['tts']
                    listenComprehensions.append({ 'prompt': prompt, 'tts': tts })
        if len(listenComprehensions) == 0:
            return
        merged = AudioSegment.empty()
        lyrics = []
        total_duration_ms = 0
        for listenComprehension in listenComprehensions:
            prompt = listenComprehension['prompt']
            audio_filename = self._get_static_filename(listenComprehension['tts'])
            lyrics.append(f"[{self._format_duration(total_duration_ms)}]{prompt}")
            audio = AudioSegment.from_mp3(audio_filename)
            merged += audio
            merged += AudioSegment.silent(2000)
            total_duration_ms += len(audio) + 2000
        merged += AudioSegment.silent(3000)
        merged.export(target_mp3_filename, format="mp3")
        with open(target_lrc_filename, 'w', encoding='utf-8') as outfile_lrc:
            for lyric in lyrics:
                outfile_lrc.write(lyric)
                outfile_lrc.write('\n')

