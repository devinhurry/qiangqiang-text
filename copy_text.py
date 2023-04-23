import os
import shutil
import sys

if __name__ == "__main__":
    # 获取命令行参数中的原始文件夹路径
    if len(sys.argv) < 2:
        print("Usage: python script.py source_dir")
        sys.exit(1)
    source_dir = sys.argv[1]

    # 目标文件夹路径
    destination_dir = "./txt"

    # 要拷贝的文件类型
    file_extensions = (".srt", ".txt")

    # 递归遍历原始文件夹中所有符合条件的文件
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(file_extensions) and root != source_dir:
                # 构造目标文件夹路径
                target_dir = os.path.join(destination_dir, os.path.relpath(root, source_dir))
                # 创建目标文件夹
                os.makedirs(target_dir, exist_ok=True)
                # 拷贝文件到目标文件夹中
                shutil.copy2(os.path.join(root, file), target_dir)
