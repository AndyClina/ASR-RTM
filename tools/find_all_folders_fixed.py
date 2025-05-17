import os
import json
import argparse
import datetime

def find_all_folders(root_path):
    """
    搜索指定根路径下的所有文件夹及其路径
    """
    folders = []
    
    for dirpath, dirnames, _ in os.walk(root_path):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            folders.append({
                "name": dirname,
                "path": full_path
            })
    
    return folders

def generate_timestamp():
    """
    生成当前时间的时间戳字符串
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def create_json_output(folders, timestamp):
    """
    创建 JSON 输出文件
    """
    output_filename = f"find_all_filesfolder_path_{timestamp}.json"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "total_folders": len(folders),
            "folders": folders
        }, f, ensure_ascii=False, indent=4)
    
    return output_filename

def create_readme(timestamp):
    """
    创建 README 文件
    """
    readme_filename = f"README_find_all_filesfolder_path{timestamp}.json"
    
    readme_content = {
        "tool_name": "文件夹搜索工具",
        "version": "1.0",
        "created_at": timestamp,
        "description": "用于搜索指定文件夹下所有的文件夹名称及路径",
        "usage": "python find_all_folders.py -p <文件夹路径>",
        "output_format": {
            "timestamp": "生成时间戳",
            "total_folders": "找到的文件夹总数",
            "folders": [
                {
                    "name": "文件夹名称",
                    "path": "文件夹完整路径"
                }
            ]
        }
    }
    
    with open(readme_filename, 'w', encoding='utf-8') as f:
        json.dump(readme_content, f, ensure_ascii=False, indent=4)
    
    return readme_filename

def main():
    parser = argparse.ArgumentParser(description='搜索指定文件夹下的所有文件夹')
    parser.add_argument('-p', '--path', required=True, help='要搜索的文件夹路径')
    
    args = parser.parse_args()
    root_path = args.path
    
    if not os.path.isdir(root_path):
        print(f"错误: 指定的路径 '{root_path}' 不是一个有效的文件夹")
        return
    
    print(f"正在搜索文件夹: {root_path}")
    folders = find_all_folders(root_path)
    
    timestamp = generate_timestamp()
    
    json_file = create_json_output(folders, timestamp)
    readme_file = create_readme(timestamp)
    
    print(f"找到 {len(folders)} 个文件夹")
    print(f"结果已存储到: {json_file}")
    print(f"README 文件已存储到: {readme_file}")

if __name__ == "__main__":
    main()