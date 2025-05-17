#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件搜索工具：搜索指定目录下所有文件及其路径
输出为JSON格式，包含时间戳
"""

import os
import json
import argparse
import fnmatch
from datetime import datetime
from pathlib import Path


def search_files(directory, patterns=None, exclude_patterns=None, include_hidden=False, max_depth=None):
    """
    搜索指定目录下所有文件及其路径
    
    Args:
        directory: 要搜索的目录路径
        patterns: 文件匹配模式列表，如["*.py", "*.txt"]
        exclude_patterns: 要排除的文件匹配模式列表
        include_hidden: 是否包含隐藏文件
        max_depth: 最大搜索深度，为None时不限制
        
    Returns:
        包含文件信息的列表，每个文件信息是一个字典，包含名称和路径
    """
    files_info = []
    start_depth = directory.count(os.sep)
    
    try:
        # 使用os.walk遍历目录及其子目录
        for root, dirs, files in os.walk(directory):
            # 计算当前目录的深度
            current_depth = root.count(os.sep) - start_depth
            
            # 检查是否超过最大深度
            if max_depth is not None and current_depth > max_depth:
                dirs.clear()  # 清空目录列表，停止更深层次的遍历
                continue
                
            # 如果不包含隐藏目录，过滤掉隐藏目录
            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                # 如果不包含隐藏文件，跳过隐藏文件
                if not include_hidden and file.startswith('.'):
                    continue
                    
                # 获取完整路径
                file_path = os.path.join(root, file)
                # 将路径转换为标准格式
                file_path = os.path.normpath(file_path)
                
                # 如果有指定匹配模式，检查是否符合
                if patterns:
                    if not any(fnmatch.fnmatch(file, pattern) for pattern in patterns):
                        continue
                
                # 如果有指定排除模式，检查是否符合排除条件
                if exclude_patterns:
                    if any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                        continue
                
                # 获取文件大小和修改时间
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                file_modified = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                
                # 获取相对路径
                rel_path = os.path.relpath(file_path, directory)
                
                # 添加文件信息到列表
                files_info.append({
                    "name": file,
                    "path": file_path,
                    "relative_path": rel_path,
                    "size": file_size,
                    "size_human": format_size(file_size),
                    "modified": file_modified,
                    "depth": current_depth
                })
    except Exception as e:
        print(f"搜索文件时出错: {str(e)}")
    
    return files_info


def format_size(size_bytes):
    """将字节大小格式化为人类可读的形式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0 or unit == 'TB':
            break
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} {unit}"


def save_to_json(data, output_dir="tools"):
    """
    将数据保存为JSON文件
    
    Args:
        data: 要保存的数据
        output_dir: 输出目录
    
    Returns:
        保存的文件路径
    """
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成带时间戳的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"find_all_files_path_{timestamp}.json"
        file_path = os.path.join(output_dir, filename)
        
        # 写入JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    except Exception as e:
        print(f"保存JSON文件时出错: {str(e)}")
        return None


def main():
    """
    主函数
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="搜索指定目录下所有文件及其路径")
    parser.add_argument(
        "directory", 
        help="要搜索的目录路径"
    )
    parser.add_argument(
        "-o", "--output-dir", 
        default="tools", 
        help="输出目录，默认为tools"
    )
    parser.add_argument(
        "-p", "--patterns", 
        nargs="*", 
        help="文件匹配模式，如 '*.py' '*.txt'"
    )
    parser.add_argument(
        "-e", "--exclude", 
        nargs="*", 
        help="排除的文件模式，如 '*.pyc' '*.bak'"
    )
    parser.add_argument(
        "--hidden", 
        action="store_true", 
        help="包含隐藏文件和目录"
    )
    parser.add_argument(
        "--depth", 
        type=int, 
        help="最大搜索深度"
    )
    parser.add_argument(
        "--sort", 
        choices=["name", "path", "size", "modified"], 
        help="排序方式"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    directory = args.directory
    output_dir = args.output_dir
    
    # 检查目录是否存在
    if not os.path.exists(directory) or not os.path.isdir(directory):
        print(f"错误：目录 {directory} 不存在或不是一个有效的目录")
        return
    
    print(f"搜索目录: {directory}")
    if args.patterns:
        print(f"匹配模式: {', '.join(args.patterns)}")
    if args.exclude:
        print(f"排除模式: {', '.join(args.exclude)}")
    if args.hidden:
        print("包含隐藏文件和目录")
    if args.depth is not None:
        print(f"最大搜索深度: {args.depth}")
    
    print("开始搜索文件...")
    
    # 搜索文件
    files_info = search_files(
        directory, 
        patterns=args.patterns, 
        exclude_patterns=args.exclude, 
        include_hidden=args.hidden,
        max_depth=args.depth
    )
    
    # 排序结果
    if args.sort and files_info:
        if args.sort == "name":
            files_info.sort(key=lambda x: x["name"])
        elif args.sort == "path":
            files_info.sort(key=lambda x: x["path"])
        elif args.sort == "size":
            files_info.sort(key=lambda x: x["size"])
        elif args.sort == "modified":
            files_info.sort(key=lambda x: x["modified"])
    
    print(f"找到 {len(files_info)} 个文件")
    
    # 保存结果
    if files_info:
        result = {
            "search_directory": os.path.abspath(directory),
            "file_count": len(files_info),
            "search_params": {
                "patterns": args.patterns,
                "exclude_patterns": args.exclude,
                "include_hidden": args.hidden,
                "max_depth": args.depth,
                "sort": args.sort
            },
            "files": files_info,
            "timestamp": datetime.now().isoformat()
        }
        output_file = save_to_json(result, output_dir)
        if output_file:
            print(f"文件列表已保存至: {output_file}")
    else:
        print("未找到任何文件或搜索过程中出错")


if __name__ == "__main__":
    main()