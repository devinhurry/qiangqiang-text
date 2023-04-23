# 网页中的时间并不是音频的真正时间,再把日期减一
# 读取文件夹下的txt文件, 开头是日期,把日期减一,用新的日期替换老的日期
# 然后重命名
import os
import sys
import datetime

# 获取命令行参数中的 source_dir
source_dir = sys.argv[1]

# 获取文件夹中所有的 .txt 文件名
files = [f for f in os.listdir(source_dir) if f.endswith('.txt')]

# 遍历所有的 .txt 文件并重命名
for file in files:
    file_path = os.path.join(source_dir, file)
    # 读取文件内容
    with open(file_path, 'r') as f:
        content = f.read()
    # 匹配文件开头的日期
    old_date_str = file.split(' ')[0]
    old_date = datetime.datetime.strptime(old_date_str, '%Y%m%d').date()
    # 将日期减一
    new_date = old_date - datetime.timedelta(days=1)
    # 生成新的文件名并重命名文件
    new_file_name = new_date.strftime('%Y%m%d') + ' ' + ' '.join(file.split(' ')[1:])
    new_file_path = os.path.join(source_dir, new_file_name)
    os.rename(file_path, new_file_path)
