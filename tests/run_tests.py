"""
测试运行脚本
用于执行所有测试并生成报告
"""

import os
import sys
import json
import wave
import psutil
import logging
import importlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def setup_logging() -> None:
    """设置日志记录"""
    # 创建logs目录（如果不存在）
    log_dir = os.path.join(project_root, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 生成带时间戳的日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"test_run_{timestamp}.log")
    
    # 配置日志记录
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info(f"测试开始运行 - {datetime.now()}")
    logging.info(f"日志文件: {log_file}")

def check_environment() -> Dict[str, Any]:
    """检查运行环境"""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
    except ImportError:
        cuda_available = False

    checks = {
        "Python版本": sys.version.split()[0],
        "CUDA可用": cuda_available,
        "CPU线程数": os.cpu_count(),
        "系统内存": f"{psutil.virtual_memory().total / (1024**3):.1f}GB",
        "当前目录": os.getcwd(),
        "项目根目录": project_root,
        "Python路径": sys.executable,
        "系统平台": sys.platform
    }
    return checks

def check_dependencies() -> Dict[str, str]:
    """检查必要的依赖项"""
    required_packages = {
        "sherpa_onnx": "语音识别引擎",
        "vosk": "语音识别引擎",
        "PyQt5": "图形界面",
        "numpy": "数学计算",
        "sounddevice": "音频处理",
        "torch": "深度学习支持",
        "psutil": "系统监控",
        "onnxruntime": "ONNX运行时",
        "argostranslate": "翻译引擎"
    }
    
    results = {}
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            version = importlib.import_module(package).__version__ if hasattr(importlib.import_module(package), '__version__') else "版本未知"
            results[package] = f"已安装 ({version})"
        except ImportError as e:
            results[package] = f"未安装 - {description} ({str(e)})"
    
    return results

def check_audio_devices() -> Dict[str, Any]:
    """检查音频设备"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        results = {
            "默认输入设备": sd.default.device[0],
            "默认输出设备": sd.default.device[1],
            "可用设备数量": len(devices)
        }
        
        # 添加详细设备信息
        for i, device in enumerate(devices):
            results[f"设备_{i}"] = f"{device['name']} ({device['max_input_channels']}in/{device['max_output_channels']}out)"
        
        return results
    except Exception as e:
        return {"错误": f"音频设备检查失败: {str(e)}"}

def verify_config_files() -> Dict[str, str]:
    """验证配置文件完整性"""
    config_files = {
        "主配置文件": os.path.join(project_root, "config", "config.json"),
        "模型配置文件": os.path.join(project_root, "config", "models.json")
    }
    
    results = {}
    for name, path in config_files.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if name == "主配置文件":
                    # 验证主配置文件结构
                    required_sections = ["transcription", "ui", "logging", "performance"]
                    if all(section in config for section in required_sections):
                        # 验证默认模型设置
                        if config["transcription"]["default_model"] == "vosk_small":
                            results[name] = "正常"
                        else:
                            results[name] = "错误: 默认模型设置不正确"
                    else:
                        results[name] = "错误: 缺少必要的配置项"
                elif name == "模型配置文件":
                    # 验证模型配置文件结构
                    if "asr" in config and "translation" in config:
                        # 验证是否包含所有必需的模型
                        required_asr_models = ["vosk_small", "sherpa_0220_int8", "sherpa_0220_std", 
                                            "sherpa_0626_int8", "sherpa_0626_std"]
                        required_translation_models = ["opus", "argos"]
                        
                        if all(model in config["asr"] for model in required_asr_models) and \
                           all(model in config["translation"] for model in required_translation_models):
                            results[name] = "正常"
                        else:
                            results[name] = "错误: 缺少必要的模型配置"
                    else:
                        results[name] = "错误: 缺少必要的配置项"
        except Exception as e:
            results[name] = f"错误: {str(e)}"
    
    return results

def verify_test_files() -> Dict[str, str]:
    """验证测试音频文件"""
    # 更新为新的测试音频目录
    test_audio_dir = "C:\\Users\\crige\\models\\test_data"
    results = {}
    
    # 检查目录是否存在
    if not os.path.exists(test_audio_dir):
        results["测试目录"] = f"错误: 目录不存在 {test_audio_dir}"
        return results
        
    # 检查默认测试文件
    default_test_file = os.path.join(test_audio_dir, "mytest.mp4")
    if os.path.exists(default_test_file):
        results["默认测试文件"] = f"找到: {default_test_file}"
    else:
        results["默认测试文件"] = f"错误: 文件不存在 {default_test_file}"
    
    # 检查音频文件
    test_files = {
        "MP4文件": "*.mp4",
        "WAV文件": "*.wav"
    }
    
    for file_type, pattern in test_files.items():
        files = list(Path(test_audio_dir).glob(pattern))
        if files:
            results[file_type] = f"找到 {len(files)} 个文件"
            # 验证每个音频文件
            for file in files:
                if file_type == "WAV文件":
                    try:
                        with wave.open(str(file), 'rb') as wav:
                            channels = wav.getnchannels()
                            sample_width = wav.getsampwidth()
                            frame_rate = wav.getframerate()
                            results[f"{file.name}"] = f"声道:{channels},采样率:{frame_rate}Hz"
                    except Exception as e:
                        results[f"{file.name}"] = f"无效的WAV文件: {str(e)}"
                else:
                    results[f"{file.name}"] = "找到文件"
        else:
            results[file_type] = "未找到文件"
    
    return results

def check_main_program() -> Dict[str, str]:
    """检查主程序环境"""
    results = {}
    
    # 检查主程序文件
    main_file = os.path.join(project_root, "main.py")
    results["主程序文件"] = "存在" if os.path.exists(main_file) else "不存在"
    
    # 检查必要目录
    directories = {
        "配置目录": os.path.join(project_root, "config"),
        "日志目录": os.path.join(project_root, "logs"),
        "插件目录": os.path.join(project_root, "src", "core", "plugins"),
        "UI目录": os.path.join(project_root, "src", "ui"),
        "工具目录": os.path.join(project_root, "src", "utils")
    }
    
    for name, path in directories.items():
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                results[name] = "已创建"
            except Exception as e:
                results[name] = f"创建失败: {str(e)}"
        else:
            results[name] = "存在"
    
    return results

def verify_models() -> Dict[str, str]:
    """验证模型文件"""
    try:
        with open(os.path.join(project_root, "config", "models.json"), 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        return {"错误": f"无法读取模型配置: {str(e)}"}
    
    results = {}
    for model_type, models in config.items():
        for model_name, model_config in models.items():
            path = model_config.get('path', '')
            if not os.path.exists(path):
                results[model_name] = f"路径不存在: {path}"
                continue
            
            if model_type == "asr":
                # 检查ASR模型文件
                required_files = []
                if "encoder" in model_config:
                    required_files.extend([
                        model_config.get('encoder', ''),
                        model_config.get('decoder', ''),
                        model_config.get('joiner', ''),
                        model_config.get('tokens', '')
                    ])
                
                missing_files = []
                for file in required_files:
                    if file and not os.path.exists(os.path.join(path, file)):
                        missing_files.append(file)
                
                if missing_files:
                    results[model_name] = f"缺失文件: {', '.join(missing_files)}"
                else:
                    results[model_name] = "正常"
            
            elif model_type == "translation":
                # 检查翻译模型文件
                if os.path.exists(path):
                    results[model_name] = "正常"
                else:
                    results[model_name] = f"路径不存在: {path}"
    
    return results

def run_pre_test_checks() -> bool:
    """运行测试前检查"""
    logging.info("=== 开始测试前检查 ===")
    
    # 1. 环境检查
    env_results = check_environment()
    logging.info("\n环境信息:")
    for key, value in env_results.items():
        logging.info(f"- {key}: {value}")
    
    # 2. 依赖项检查
    dep_results = check_dependencies()
    logging.info("\n依赖项检查:")
    for name, status in dep_results.items():
        logging.info(f"- {name}: {status}")
    
    # 3. 音频设备检查
    audio_results = check_audio_devices()
    logging.info("\n音频设备检查:")
    for name, status in audio_results.items():
        logging.info(f"- {name}: {status}")
    
    # 4. 主程序环境检查
    main_results = check_main_program()
    logging.info("\n主程序环境检查:")
    for name, status in main_results.items():
        logging.info(f"- {name}: {status}")
    
    # 5. 配置文件检查
    config_results = verify_config_files()
    logging.info("\n配置文件检查:")
    for name, status in config_results.items():
        logging.info(f"- {name}: {status}")
    
    # 6. 测试文件检查
    test_results = verify_test_files()
    logging.info("\n测试文件检查:")
    for name, status in test_results.items():
        logging.info(f"- {name}: {status}")
    
    # 7. 模型文件检查
    model_results = verify_models()
    logging.info("\n模型文件检查:")
    for name, status in model_results.items():
        logging.info(f"- {name}: {status}")
    
    # 判断是否所有检查都通过
    all_passed = (
        all("未安装" not in status for status in dep_results.values()) and
        "错误" not in str(audio_results.values()) and
        all(status in ["存在", "已创建"] for status in main_results.values()) and
        all(status == "正常" for status in config_results.values()) and
        "错误" not in str(test_results.values()) and
        all(status == "正常" for status in model_results.values())
    )
    
    # 记录检查结果
    if all_passed:
        logging.info("✅ 所有检查通过")
    else:
        logging.error("⚠️ 检查未通过")
    
    return all_passed

def analyze_test_log(log_file: str) -> Dict[str, Any]:
    """分析测试日志文件"""
    analysis = {
        "运行时间": None,
        "检查结果": {
            "环境信息": [],
            "依赖项检查": [],
            "音频设备检查": [],
            "主程序环境检查": [],
            "配置文件检查": [],
            "测试文件检查": [],
            "模型文件检查": []
        },
        "错误数": 0,
        "警告数": 0,
        "错误详情": [],
        "警告详情": [],
        "总体状态": "未知"
    }
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_section = None
        
        for line in lines:
            # 解析每行日志
            if " - ERROR - " in line:
                analysis["错误数"] += 1
                analysis["错误详情"].append(line.strip())
            elif " - WARNING - " in line:
                analysis["警告数"] += 1
                analysis["警告详情"].append(line.strip())
            
            # 识别检查部分
            if "\n环境信息:" in line:
                current_section = "环境信息"
            elif "\n依赖项检查:" in line:
                current_section = "依赖项检查"
            elif "\n音频设备检查:" in line:
                current_section = "音频设备检查"
            elif "\n主程序环境检查:" in line:
                current_section = "主程序环境检查"
            elif "\n配置文件检查:" in line:
                current_section = "配置文件检查"
            elif "\n测试文件检查:" in line:
                current_section = "测试文件检查"
            elif "\n模型文件检查:" in line:
                current_section = "模型文件检查"
            
            # 收集每个部分的信息
            if current_section and "- " in line:
                item = line.split("- ")[-1].strip()
                analysis["检查结果"][current_section].append(item)
            
            # 检查总体状态
            if "✅ 所有检查通过" in line:
                analysis["总体状态"] = "通过"
            elif "⚠️ 检查未通过" in line:
                analysis["总体状态"] = "未通过"
                
        return analysis
        
    except Exception as e:
        logging.error(f"日志分析失败: {str(e)}")
        return analysis

def print_analysis_report(analysis: Dict[str, Any]) -> None:
    """打印分析报告"""
    print("\n=== 测试日志分析报告 ===")
    print(f"总体状态: {analysis['总体状态']}")
    print(f"错误数: {analysis['错误数']}")
    print(f"警告数: {analysis['警告数']}")
    
    print("\n=== 详细检查结果 ===")
    for section, items in analysis["检查结果"].items():
        if items:  # 只显示有内容的部分
            print(f"\n{section}:")
            for item in items:
                print(f"  - {item}")
    
    if analysis["错误详情"]:
        print("\n=== 错误详情 ===")
        for error in analysis["错误详情"]:
            print(f"  {error}")
            
    if analysis["警告详情"]:
        print("\n=== 警告详情 ===")
        for warning in analysis["警告详情"]:
            print(f"  {warning}")

def run_main_program_tests() -> Dict[str, bool]:
    """运行主程序测试"""
    test_results = {}
    
    try:
        # 1. 导入主程序 - 修改导入路径
        logging.info("测试主程序导入...")
        sys.path.insert(0, project_root)  # 确保能找到主程序
        from main import RTMApplication  # 直接从根目录导入
        test_results["主程序导入"] = True
        
        # 2. 测试创建应用实例
        logging.info("测试创建应用实例...")
        app = RTMApplication()
        test_results["应用实例创建"] = True
        
        # 3. 测试加载配置
        logging.info("测试加载配置...")
        config_loaded = app.load_config()
        test_results["配置加载"] = config_loaded
        
        # 4. 测试加载ASR模型
        logging.info("测试加载ASR模型...")
        asr_loaded = app.load_asr_model()
        test_results["ASR模型加载"] = asr_loaded
        
        # 5. 测试加载翻译模型
        logging.info("测试加载翻译模型...")
        translation_loaded = app.load_translation_model()
        test_results["翻译模型加载"] = translation_loaded
        
        return test_results
        
    except Exception as e:
        logging.error(f"主程序测试失败: {str(e)}")
        return {"错误": str(e)}

def main():
    """主函数"""
    # 设置日志记录
    setup_logging()
    
    try:
        if not run_pre_test_checks():
            logging.error("前置检查未通过，请修复上述问题后再运行测试")
            sys.exit(1)
        
        logging.info("✅ 前置检查通过，开始运行测试...")
        
        # 运行主程序测试
        logging.info("=== 开始主程序测试 ===")
        test_results = run_main_program_tests()
        
        # 记录测试结果
        logging.info("\n主程序测试结果:")
        for test_name, result in test_results.items():
            if result is True:
                logging.info(f"✅ {test_name}: 通过")
            else:
                logging.error(f"❌ {test_name}: 失败")
        
        logging.info("=== 测试执行完成 ===")
        
        # 分析测试日志
        log_file = logging.getLogger().handlers[0].baseFilename
        analysis = analyze_test_log(log_file)
        print_analysis_report(analysis)
        
    except Exception as e:
        logging.exception(f"测试运行过程中出现错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()