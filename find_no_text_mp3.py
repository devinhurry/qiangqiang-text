import sys
import os
import fnmatch
import shutil

# 从命令行参数中获取要读取的文件夹路径
if len(sys.argv) < 2:
    print('Usage: python script.py folder')
    sys.exit(1)

folder = sys.argv[1]

# 指定要匹配的文件名模式
pattern = '*.mp3'

# 列出指定文件夹中匹配的MP3文件
mp3_files = []
for root, dirs, files in os.walk(folder):
    for filename in fnmatch.filter(files, pattern):
        mp3_files.append(os.path.join(root, filename))

# 检查每个MP3文件是否存在相应的TXT文件
for mp3_file in mp3_files:
    txt_file = os.path.splitext(mp3_file)[0] + '.txt'
    srt_file = os.path.splitext(mp3_file)[0] + '.srt'
    if not os.path.exists(os.path.join(folder, txt_file)) and not os.path.exists(os.path.join(folder, srt_file)):
        shutil.copy(mp3_file, 'tmp')
        print(os.path.basename(mp3_file))