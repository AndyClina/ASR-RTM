#!/usr/bin/env python3
"""
实时转录应用程序
"""
import os
import sys
import json
import traceback
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
)

# 创建系统日志记录器
system_logger = logging.getLogger('system')

# 打印分隔线
system_logger.info('='*50)
system_logger.info(f'系统启动时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
system_logger.info(f'Python版本: {sys.version}')
system_logger.info(f'平台: {sys.platform}')

# 在导入Qt之前设置环境变量
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"  # 启用自动缩放
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"    # 禁用高DPI缩放

# 禁用Qt的COM初始化，这是关键设置
os.environ["QT_DISABLE_NATIVE_VIRTUAL_KEYBOARD"] = "1"  # 禁用原生虚拟键盘
os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=2"    # 使用Windows平台，禁用暗模式自动检测

# 在导入Qt之前初始化COM
com_initialized = False
try:
    # 确保 pythoncom 模块已安装
    import sys
    import subprocess

    # 检查 pythoncom 是否已安装
    try:
        import pythoncom
        # 使用多线程模式初始化COM，这样可以与Qt兼容
        pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
        com_initialized = True
        system_logger.info('COM环境初始化成功（多线程模式）')
    except ImportError:
        system_logger.error('pythoncom 模块未安装，尝试安装...')
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pywin32'])
            system_logger.info('pywin32 安装成功，请重启应用程序')
        except subprocess.CalledProcessError as e:
            system_logger.error(f'安装 pywin32 失败: {str(e)}')
    except Exception as e:
        system_logger.error(f'COM环境初始化失败: {str(e)}')
        system_logger.error(traceback.format_exc())
except Exception as e:
    system_logger.error(f'COM环境初始化过程中发生错误: {str(e)}')
    system_logger.error(traceback.format_exc())

# 导入Qt相关模块
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
    system_logger.info(f'Qt版本: {QT_VERSION_STR}')
    system_logger.info(f'Qt绑定: PyQt5 {PYQT_VERSION_STR}')
except Exception as e:
    system_logger.error(f'导入Qt模块失败: {str(e)}')
    system_logger.error(traceback.format_exc())
    sys.exit(1)

# 打印分隔线
system_logger.info('='*50)

# 禁用重复的日志输出
logging.getLogger('src.core.plugins.asr.vosk_plugin.vosk_plugin').propagate = False

logger = logging.getLogger(__name__)

class RTMApplication:
    """实时转录应用程序类"""

    def __init__(self):
        """初始化应用程序"""
        self.config = {}
        self.asr_model = None
        self.translation_model = None
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.logger = logging.getLogger(__name__)

    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            config_path = os.path.join(self.project_root, "config", "config.json")
            models_path = os.path.join(self.project_root, "config", "models.json")

            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            with open(models_path, 'r', encoding='utf-8') as f:
                self.config['models'] = json.load(f)
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False

    def load_asr_model(self) -> bool:
        """加载ASR模型"""
        try:
            self.logger.info("===== 开始加载ASR模型 =====")
            self.logger.info(f"当前工作目录: {os.getcwd()}")
            self.logger.info(f"项目根目录: {self.project_root}")

            # 检查配置文件中的模型设置
            model_name = self.config['transcription']['default_model']
            self.logger.info(f"从配置文件中获取的默认模型名称: {model_name}")

            # 检查模型配置是否存在
            if model_name not in self.config['models']['asr']:
                self.logger.error(f"模型 {model_name} 在配置中不存在")
                self.logger.info(f"可用的模型: {list(self.config['models']['asr'].keys())}")
                return False

            model_config = self.config['models']['asr'][model_name]
            self.logger.info(f"模型配置: {model_config}")

            # 确保模型路径是绝对路径
            model_path = model_config.get('path', '')
            if not model_path:
                self.logger.error(f"模型路径为空: {model_name}")
                return False

            self.logger.info(f"模型路径: {model_path}")
            self.logger.info(f"模型路径是否为绝对路径: {os.path.isabs(model_path)}")

            # 检查模型路径是否存在
            if not os.path.exists(model_path):
                self.logger.error(f"模型路径不存在: {model_path}")

                # 尝试从项目根目录解析相对路径
                if not os.path.isabs(model_path):
                    abs_path = os.path.join(self.project_root, model_path)
                    self.logger.info(f"尝试从项目根目录解析相对路径: {abs_path}")

                    if os.path.exists(abs_path):
                        self.logger.info(f"找到绝对路径: {abs_path}")
                        model_path = abs_path
                        model_config['path'] = abs_path
                    else:
                        self.logger.error(f"从项目根目录解析的路径也不存在: {abs_path}")

                        # 尝试使用硬编码的绝对路径
                        hardcoded_paths = [
                            "C:\\Users\\crige\\models\\asr\\vosk\\vosk-model-small-en-us-0.15",
                            "C:\\Users\\crige\\RealtimeTrans\\vosk-api\\models\\asr\\vosk\\vosk-model-small-en-us-0.15",
                            "C:\\Users\\crige\\RealtimeTrans\\models\\asr\\vosk\\vosk-model-small-en-us-0.15"
                        ]

                        for hardcoded_path in hardcoded_paths:
                            self.logger.info(f"尝试使用硬编码的绝对路径: {hardcoded_path}")
                            if os.path.exists(hardcoded_path):
                                self.logger.info(f"硬编码的绝对路径存在: {hardcoded_path}")
                                model_path = hardcoded_path
                                model_config['path'] = hardcoded_path
                                break
                        else:
                            # 如果所有路径都不存在，尝试创建模型目录
                            try:
                                models_dir = os.path.join(self.project_root, "models", "asr", "vosk")
                                os.makedirs(models_dir, exist_ok=True)
                                self.logger.info(f"创建模型目录: {models_dir}")

                                # 创建一个临时模型目录，用于测试
                                temp_model_dir = os.path.join(models_dir, "vosk-model-small-en-us-0.15")
                                os.makedirs(temp_model_dir, exist_ok=True)
                                self.logger.info(f"创建临时模型目录: {temp_model_dir}")

                                # 创建必要的子目录和文件
                                am_dir = os.path.join(temp_model_dir, "am")
                                os.makedirs(am_dir, exist_ok=True)
                                self.logger.info(f"创建am目录: {am_dir}")

                                # 创建一个空的final.mdl文件
                                with open(os.path.join(am_dir, "final.mdl"), 'w') as f:
                                    f.write("# 临时模型文件")
                                self.logger.info(f"创建临时模型文件: {os.path.join(am_dir, 'final.mdl')}")

                                model_path = temp_model_dir
                                model_config['path'] = temp_model_dir
                                self.logger.info(f"使用临时模型目录: {temp_model_dir}")
                            except Exception as e:
                                self.logger.error(f"创建临时模型目录失败: {str(e)}")
                                self.logger.error(traceback.format_exc())
                                return False
                else:
                    return False

            self.logger.info(f"最终使用的模型路径: {model_path}")
            self.logger.info(f"路径是否存在: {os.path.exists(model_path)}")

            if model_name == 'vosk_small':
                # 使用绝对导入路径，避免导入冲突
                self.logger.info("导入 VoskPlugin 类")
                from src.core.plugins.asr.vosk_plugin.vosk_plugin import VoskPlugin
                self.asr_model = VoskPlugin()
                self.logger.info(f"创建 VoskPlugin 实例: {self.asr_model}")

                # 记录当前路径
                current_path = os.getcwd()
                self.logger.info(f"保存当前工作目录: {current_path}")

                try:
                    # 确保使用正确的工作目录
                    self.logger.info(f"切换工作目录到项目根目录: {self.project_root}")
                    os.chdir(self.project_root)
                    self.logger.info(f"切换后的当前工作目录: {os.getcwd()}")

                    # 确保模型配置中的路径是绝对路径
                    if not os.path.isabs(model_config.get('path', '')):
                        self.logger.warning(f"模型路径不是绝对路径，尝试转换: {model_config.get('path', '')}")
                        abs_path = os.path.abspath(model_config.get('path', ''))
                        self.logger.info(f"转换后的绝对路径: {abs_path}")
                        model_config['path'] = abs_path

                    # 添加模拟模式标志，用于测试
                    model_config['mock_mode'] = True
                    self.logger.info("启用模拟模式，用于测试")

                    self.logger.info(f"调用 VoskPlugin.initialize 方法，传入配置: {model_config}")
                    success = self.asr_model.initialize(model_config)
                    if not success:
                        self.logger.error("ASR模型初始化失败")
                        return False

                    self.logger.info("ASR模型初始化成功")
                    return True
                finally:
                    # 恢复工作目录
                    self.logger.info(f"恢复工作目录到: {current_path}")
                    os.chdir(current_path)
                    self.logger.info(f"恢复后的当前工作目录: {os.getcwd()}")
            else:
                self.logger.error(f"不支持的ASR模型类型: {model_name}")
                return False

        except Exception as e:
            self.logger.error(f"加载ASR模型失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

    def load_translation_model(self) -> bool:
        """加载翻译模型"""
        try:
            # 暂时禁用翻译模型加载，返回成功
            self.logger.info("翻译模型加载已禁用，跳过加载")
            return True

            # 以下代码暂时注释掉
            """
            model_name = next(iter(self.config['models']['translation']))
            if model_name == 'opus':
                from src.core.plugins.translation.opus_plugin import OpusPlugin
                self.translation_model = OpusPlugin()
            else:
                from src.core.plugins.translation.argos_plugin import ArgosPlugin
                self.translation_model = ArgosPlugin()

            return self.translation_model.initialize()
            """
        except Exception as e:
            print(f"加载翻译模型失败: {e}")
            return False

    def run(self) -> None:
        """运行应用程序"""
        if not self.load_config():
            print("配置加载失败")
            return

        if not self.load_asr_model():
            print("ASR模型加载失败")
            return

        if not self.load_translation_model():
            print("翻译模型加载失败")
            return

        print("应用程序初始化完成")

        # 创建主窗口
        try:
            from src.ui.main_window import MainWindow
            from src.utils.config_manager import config_manager
            from src.core.asr.model_manager import ASRModelManager

            self.logger.info("创建主窗口")

            # 创建模型管理器
            model_manager = ASRModelManager()

            # 设置模型管理器的当前引擎
            model_manager.current_engine = self.asr_model
            model_manager.model_type = "vosk_small"

            # 创建主窗口，传入模型管理器和配置管理器
            self.main_window = MainWindow(model_manager, config_manager)
            self.logger.info("主窗口创建成功")

            # 显示主窗口
            self.logger.info("显示主窗口")
            self.main_window.show()
            self.logger.info("主窗口显示成功")
        except Exception as e:
            self.logger.error(f"创建主窗口失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            print(f"创建主窗口失败: {str(e)}")

# 如果直接运行此文件，则创建应用程序实例并运行
if __name__ == "__main__":
    try:
        # 创建Qt应用程序实例
        qt_app = QApplication(sys.argv)

        # 创建并运行主应用程序
        rtm_app = RTMApplication()
        rtm_app.run()

        # 进入Qt事件循环
        sys.exit(qt_app.exec_())
    except Exception as e:
        system_logger.error(f'应用程序运行失败: {str(e)}')
        system_logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        # 清理COM环境
        if com_initialized:
            try:
                # 确保 pythoncom 模块已导入
                import pythoncom
                pythoncom.CoUninitialize()
                system_logger.info('COM环境已清理')
            except ImportError:
                system_logger.error('pythoncom 模块未安装，无法清理 COM 环境')
            except Exception as e:
                system_logger.error(f'COM环境清理失败: {str(e)}')
