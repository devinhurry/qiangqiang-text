import os
import difflib
import sys
from pypinyin import pinyin, lazy_pinyin, Style
if len(sys.argv) < 2:
    print('Usage: python compare_files.py <folder_path>')
    sys.exit()

# 从命令行参数获取文件夹路径
folder_path = sys.argv[1]

# 读取文件夹下的所有文件
file_list = os.listdir(folder_path)

# 按日期和文件类型分类
file_dict = {}
for file_name in file_list:
    file_path = os.path.join(folder_path, file_name)
    if os.path.isfile(file_path):
        file_date = file_name[:8]
        file_type = file_name[-3:].lower()
        if file_type == 'mp3' or file_type == 'txt':
            if file_date not in file_dict:
                file_dict[file_date] = {}
            if file_type not in file_dict[file_date]:
                file_dict[file_date][file_type] = []
            file_dict[file_date][file_type].append(file_path)

# 比较文件名相似度并重命名 txt 文件
for date, type_dict in file_dict.items():
    if 'mp3' in type_dict and 'txt' in type_dict:

        mp3_files = [os.path.join(folder_path, file) for file in type_dict['mp3']]
        txt_files = [os.path.join(folder_path, file) for file in type_dict['txt']]
        for txt_file in txt_files:
            txt_episode_name = os.path.splitext(os.path.basename(txt_file))[0][8:]
            for mp3_file in mp3_files:
                mp3_episode_name = os.path.splitext(os.path.basename(mp3_file))[0][8:]
                similarity = difflib.SequenceMatcher(None, txt_episode_name, mp3_episode_name).ratio()
                if similarity > 0 and similarity != 1:
                    new_txt_file_name = date + mp3_episode_name + '.txt'
                    new_txt_file_path = os.path.join(folder_path, new_txt_file_name)
                    if similarity > 0.1:
                        os.rename(txt_file, new_txt_file_path)
                        print('Renamed', os.path.basename(txt_file), 'to', new_txt_file_name)
                        continue
                    if len(sys.argv) > 2 and (sys.argv[2] == '--gen' or sys.argv[2] == '--rename'):
                        print(f"Generate Text For Mp3 {mp3_episode_name}")
                        trimmed_mp3_file = f"/tmp/{mp3_episode_name}.mp3"
                        trimmed_speech_to_txt_file = f"/tmp/{mp3_episode_name}.txt"

                        if not os.path.exists(trimmed_speech_to_txt_file):
                            print('Date:', date)
                            cmd = f"ffmpeg -ss 10 -t 20  -i \"{mp3_file}\" \"{trimmed_mp3_file}\""
                            print(cmd)
                            os.system(cmd)
                            cmd = f"whisper \"{trimmed_mp3_file}\" --language Chinese --model tiny --output_format txt --output_dir=/tmp --initial_prompt \"以下是普通话的句子\""
                            print(cmd)
                            os.system(cmd)

                        with open(trimmed_speech_to_txt_file) as f:
                            content = f.read()
                    
                    
                    if len(sys.argv) > 2 and sys.argv[2] == '--show':
                        print(f"mp3: {date}{mp3_episode_name}.mp3 txt: {date}{txt_episode_name}.txt")
                    if len(sys.argv) > 2 and sys.argv[2] == '--rename':
                        # 找到txt_file文件中的 "以下为文字实录" 后面的100个字符
                        # 如果没找到 就取前300个字符
                        head = ""
                        with open(txt_file, 'r') as file:
                            found = False
                            i = 0
                            for line in file:
                                if '窦文涛：' in line and i < 6:
                                    found = True
                                    text = file.read(100)
                                    l = line.replace('窦文涛：','')
                                    head = l + text[:100]
                                    break
                                i += 1
                            if not found:
                                file.seek(0)  # 回到文件开头
                                first_300 = file.read(300)
                                head = first_300

                        audio_head_pinyin = " ".join(lazy_pinyin(content.replace("\n", "")[:30]))
                        txt_head_pinyin = " ".join(lazy_pinyin(head.replace("\n", "")[:30]))
                        pinyin_sim = difflib.SequenceMatcher(None, audio_head_pinyin, txt_head_pinyin).ratio()
                        if pinyin_sim > 0.6:
                            os.rename(txt_file, new_txt_file_path)
                            print('Renamed', os.path.basename(txt_file), 'to', new_txt_file_name)                            
                            continue
                        os.system('clear')                                
                        print("\n\n\n=========")
                        print(f"\n=====AudioContent: \n{content}")
                        print(f"\n=====TextContent: \n{head}")

                        print(f"\n\n名字1: {mp3_episode_name}")
                        print(f"名字2: {txt_episode_name}")
                        print(f'拼音相似度: {pinyin_sim} y/n?')
                        # continue
                        user_input = input()
                        if user_input.lower() == 'y' or user_input.lower() == 'a':
                            os.rename(txt_file, new_txt_file_path)
                            print('Renamed', os.path.basename(txt_file), 'to', new_txt_file_name)
                        else:
                            print('Skipped', os.path.basename(txt_file))
