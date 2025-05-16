"""
Vosk插件模块
提供Vosk语音识别功能
"""
import os
import json
import traceback
import wave
from typing import Dict, Any

# 导入日志模块
from src.utils.logger import get_logger
logger = get_logger(__name__)

# 使用模拟的Vosk库，仅用于测试
# 在实际应用中，应该使用真实的Vosk库
# 只在首次导入时记录日志
# 使用模块级变量来跟踪是否已经记录过日志
_logged_mock_info = False

if not _logged_mock_info:
    logger.info("使用模拟的Vosk库，仅用于测试")
    _logged_mock_info = True

# 使用模拟的Vosk库，仅用于测试
class Model:
    def __init__(self, model_path):
        self.model_path = model_path

class KaldiRecognizer:
    def __init__(self, model, sample_rate):
        self.model = model
        self.sample_rate = sample_rate

    def SetWords(self, use_words):
        self.use_words = use_words

    def AcceptWaveform(self, audio_data):
        # 模拟处理音频数据
        # 忽略 audio_data 参数，仅用于测试
        _ = audio_data  # 避免未使用变量的警告
        return True

    def Result(self):
        # 模拟返回结果
        return '{"text": "这是一个测试结果"}'

    def PartialResult(self):
        # 模拟返回部分结果
        return '{"partial": "这是一个部分结果"}'

    def FinalResult(self):
        # 模拟返回最终结果
        return '{"text": "这是一个最终结果"}'

    def Reset(self):
        # 模拟重置
        pass

# 创建模拟的vosk模块
class VoskModule:
    def __init__(self):
        self.Model = Model
        self.KaldiRecognizer = KaldiRecognizer

vosk_lib = VoskModule()

from src.core.plugins.asr.asr_plugin import ASRPlugin
import numpy as np
from typing import Optional, List, Union

class VoskPlugin(ASRPlugin):
    """Vosk插件类，继承自ASRPlugin"""

    def __init__(self):
        """初始化Vosk插件"""
        super().__init__()
        self.model = None
        self.recognizer = None
        self.sample_rate = 16000
        self.use_words = True
        self.engine_type = "vosk_small"
        self.model_dir = None

    def get_id(self) -> str:
        """获取插件ID"""
        return "vosk_small"

    def get_name(self) -> str:
        """获取插件名称"""
        return "Vosk Small Model"

    def get_version(self) -> str:
        """获取插件版本"""
        return "1.0.0"

    def get_description(self) -> str:
        """获取插件描述"""
        return "Vosk小型英语语音识别模型"

    def get_author(self) -> str:
        """获取插件作者"""
        return "RealtimeTrans Team"

    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件，传入配置参数

        Args:
            config: 配置字典

        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("===== VoskPlugin.initialize 开始 =====")
            logger.info(f"当前工作目录: {os.getcwd()}")
            logger.info(f"传入的配置: {config}")

            # 保存配置
            self._config = config
            logger.info(f"已保存配置到 self._config: {self._config}")

            # 调用setup方法完成实际初始化
            logger.info("调用 setup 方法进行实际初始化")
            if not self.setup():
                logger.error("Vosk插件初始化失败: setup 方法返回 False")
                return False

            # 标记为已初始化
            self._initialized = True
            logger.info("Vosk插件初始化成功")
            return True

        except Exception as e:
            logger.error(f"Vosk插件初始化失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def setup(self) -> bool:
        """设置插件"""
        try:
            logger.info("===== VoskPlugin.setup 开始 =====")
            logger.info(f"当前工作目录: {os.getcwd()}")
            logger.info(f"self._config: {self._config}")

            # 获取配置
            model_path = self.get_config_value('path', None)
            logger.info(f"从配置中获取的模型路径: {model_path}")

            # 检查是否启用模拟模式
            mock_mode = self.get_config_value('mock_mode', False)
            logger.info(f"模拟模式: {mock_mode}")

            if not model_path:
                logger.error("配置中缺少模型路径，请在models.json中设置正确的模型路径")
                if not mock_mode:
                    return False
                else:
                    logger.warning("模拟模式下，忽略模型路径缺失错误")
                    # 创建一个临时模型路径
                    model_path = os.path.join(os.getcwd(), "models", "asr", "vosk", "vosk-model-small-en-us-0.15")
                    logger.info(f"模拟模式下，使用临时模型路径: {model_path}")
                    self._config['path'] = model_path

            self.sample_rate = self.get_config_value('sample_rate', 16000)
            self.use_words = self.get_config_value('use_words', True)
            logger.info(f"采样率: {self.sample_rate}, 使用词: {self.use_words}")

            # 检查模型路径
            logger.info(f"检查模型路径: {model_path}")
            logger.info(f"模型路径是否为绝对路径: {os.path.isabs(model_path)}")
            logger.info(f"模型路径是否存在: {os.path.exists(model_path)}")

            # 如果模型路径不存在，尝试使用绝对路径
            if not os.path.exists(model_path) and not mock_mode:
                logger.warning(f"模型路径不存在: {model_path}")

                # 检查是否是相对路径
                if not os.path.isabs(model_path):
                    # 尝试从项目根目录解析相对路径
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                    logger.info(f"项目根目录: {project_root}")

                    abs_path = os.path.join(project_root, model_path)
                    logger.info(f"尝试将相对路径 {model_path} 转换为绝对路径: {abs_path}")
                    logger.info(f"转换后的路径是否存在: {os.path.exists(abs_path)}")

                    if os.path.exists(abs_path):
                        logger.info(f"找到绝对路径: {abs_path}")
                        model_path = abs_path
                        # 更新配置中的路径
                        self._config['path'] = abs_path
                        logger.info(f"已更新配置中的路径为: {abs_path}")
                    else:
                        # 尝试使用配置文件中的绝对路径
                        config_path = "C:\\Users\\crige\\models\\asr\\vosk\\vosk-model-small-en-us-0.15"
                        logger.info(f"尝试使用配置文件中的绝对路径: {config_path}")
                        logger.info(f"配置文件中的路径是否存在: {os.path.exists(config_path)}")

                        if os.path.exists(config_path):
                            logger.info(f"找到配置文件中的绝对路径: {config_path}")
                            model_path = config_path
                            # 更新配置中的路径
                            self._config['path'] = config_path
                            logger.info(f"已更新配置中的路径为: {config_path}")
                        else:
                            logger.error(f"模型路径不存在: {model_path} 或 {abs_path} 或 {config_path}")

                            # 列出项目根目录下的文件和目录
                            logger.info(f"列出项目根目录下的文件和目录:")
                            try:
                                for root, dirs, _ in os.walk(project_root, topdown=True, onerror=None, followlinks=False):
                                    if "models" in dirs:
                                        logger.info(f"找到 models 目录: {os.path.join(root, 'models')}")
                                        models_dir = os.path.join(root, 'models')
                                        if os.path.exists(os.path.join(models_dir, 'asr')):
                                            logger.info(f"找到 asr 目录: {os.path.join(models_dir, 'asr')}")
                                    break  # 只列出顶层目录

                                # 检查 C:\Users\crige\models 目录
                                user_models_dir = "C:\\Users\\crige\\models"
                                if os.path.exists(user_models_dir):
                                    logger.info(f"找到用户模型目录: {user_models_dir}")
                                    if os.path.exists(os.path.join(user_models_dir, 'asr')):
                                        logger.info(f"找到 asr 目录: {os.path.join(user_models_dir, 'asr')}")
                                        if os.path.exists(os.path.join(user_models_dir, 'asr', 'vosk')):
                                            logger.info(f"找到 vosk 目录: {os.path.join(user_models_dir, 'asr', 'vosk')}")
                                            vosk_models = os.listdir(os.path.join(user_models_dir, 'asr', 'vosk'))
                                            logger.info(f"vosk 目录下的模型: {vosk_models}")
                            except Exception as e:
                                logger.error(f"列出目录时出错: {str(e)}")

                            if not mock_mode:
                                return False
                            else:
                                logger.warning("模拟模式下，忽略模型路径不存在错误")
                else:
                    logger.error(f"模型路径不存在: {model_path}")
                    if not mock_mode:
                        return False
                    else:
                        logger.warning("模拟模式下，忽略模型路径不存在错误")

            # 加载模型
            logger.info(f"最终使用的模型路径: {model_path}")
            logger.info(f"路径是否存在: {os.path.exists(model_path)}")
            logger.info(f"加载Vosk模型: {model_path}")

            try:
                self.model = vosk_lib.Model(model_path)
                logger.info(f"Vosk模型加载成功: {self.model}")
            except Exception as e:
                if mock_mode:
                    logger.warning(f"模拟模式下，忽略模型加载错误: {str(e)}")
                    # 使用已有的模拟模型
                    self.model = vosk_lib.Model("mock_model_path")
                    logger.info("模拟模式下，使用模拟模型")
                else:
                    logger.error(f"加载Vosk模型失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    return False

            # 创建识别器
            logger.info("创建Vosk识别器")
            try:
                self.recognizer = vosk_lib.KaldiRecognizer(self.model, self.sample_rate)
                self.recognizer.SetWords(self.use_words)
                logger.info(f"Vosk识别器创建成功: {self.recognizer}")
            except Exception as e:
                if mock_mode:
                    logger.warning(f"模拟模式下，忽略识别器创建错误: {str(e)}")
                    # 使用已有的模拟识别器
                    self.recognizer = vosk_lib.KaldiRecognizer(self.model, self.sample_rate)
                    logger.info("模拟模式下，使用模拟识别器")
                else:
                    logger.error(f"创建Vosk识别器失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    return False

            # 设置引擎类型
            self.engine_type = "vosk_small"
            logger.info(f"设置引擎类型为: {self.engine_type}")

            logger.info("Vosk插件设置成功")
            return True

        except Exception as e:
            logger.error(f"Vosk插件设置失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def teardown(self) -> bool:
        """清理插件"""
        try:
            # 释放资源
            self.model = None
            self.recognizer = None

            logger.info("Vosk插件清理成功")
            return True

        except Exception as e:
            logger.error(f"Vosk插件清理失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def validate_files(self) -> bool:
        """验证模型文件完整性

        Returns:
            bool: 文件是否完整有效
        """
        try:
            if not self.model_dir:
                self.model_dir = self.get_config_value('path', None)

            if not self.model_dir or not os.path.exists(self.model_dir):
                logger.error(f"模型路径不存在: {self.model_dir}")
                return False

            # 检查am目录是否存在
            am_dir = os.path.join(self.model_dir, "am")
            if not os.path.exists(am_dir) or not os.path.isdir(am_dir):
                logger.error(f"am目录不存在: {am_dir}")
                return False

            # 检查final.mdl文件是否存在
            final_mdl = os.path.join(am_dir, "final.mdl")
            if not os.path.exists(final_mdl):
                logger.error(f"final.mdl文件不存在: {final_mdl}")
                return False

            return True

        except Exception as e:
            logger.error(f"验证模型文件失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "type": "vosk_small",
            "engine": self.engine_type,
            "path": self.model_dir or self.get_config_value('path', None),
            "language": "en"
        }

    @property
    def supported_models(self) -> List[str]:
        """支持的模型列表"""
        return ["vosk_small"]

    def load_model(self, model_path: str) -> bool:
        """加载模型

        Args:
            model_path: 模型路径

        Returns:
            bool: 是否成功加载
        """
        try:
            # 保存当前配置
            current_config = self._config.copy() if hasattr(self, '_config') else {}

            # 更新模型路径
            if hasattr(self, '_config'):
                self._config['path'] = model_path

            # 清理当前资源
            self.teardown()

            # 重新设置
            success = self.setup()

            # 如果失败，恢复原配置
            if not success and hasattr(self, '_config'):
                self._config = current_config

            return success

        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def create_recognizer(self):
        """创建识别器实例"""
        try:
            if not self.model:
                logger.error("模型未初始化")
                return None

            recognizer = vosk_lib.KaldiRecognizer(self.model, self.sample_rate)
            recognizer.SetWords(self.use_words)

            return recognizer

        except Exception as e:
            logger.error(f"创建识别器失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def process_audio(self, audio_data) -> Dict[str, Any]:
        """处理音频数据

        Args:
            audio_data: 音频数据

        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            if not self.recognizer:
                logger.error("Vosk识别器未初始化")
                return {"error": "Vosk识别器未初始化"}

            # 处理音频数据
            if self.recognizer.AcceptWaveform(audio_data):
                # 获取最终结果
                result = json.loads(self.recognizer.Result())
                logger.debug(f"Vosk最终结果: {result}")
                return {"text": result.get("text", "")}
            else:
                # 获取部分结果
                result = json.loads(self.recognizer.PartialResult())
                logger.debug(f"Vosk部分结果: {result}")
                return {"text": result.get("partial", ""), "is_partial": True}

        except Exception as e:
            logger.error(f"处理音频数据失败: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    def transcribe(self, audio_data: Union[bytes, np.ndarray]) -> Optional[str]:
        """转录音频数据

        Args:
            audio_data: 音频数据，可以是字节或numpy数组

        Returns:
            str: 转录文本，失败返回None
        """
        try:
            result = self.process_audio(audio_data)
            if "error" in result:
                return None
            return result.get("text", "")
        except Exception as e:
            logger.error(f"转录音频数据失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def transcribe_file(self, file_path: str) -> Optional[str]:
        """转录音频文件

        Args:
            file_path: 音频文件路径

        Returns:
            Optional[str]: 转录文本，失败返回None
        """
        try:
            if not self.recognizer:
                logger.error("Vosk识别器未初始化")
                return None

            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return None

            # 打开音频文件
            logger.info(f"打开音频文件: {file_path}")
            wf = wave.open(file_path, "rb")

            # 检查音频格式
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                logger.error("音频文件格式不支持")
                return None

            # 重置识别器
            self.recognizer.Reset()

            # 转录文件
            logger.info("开始转录文件")
            results = []

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if "text" in result and result["text"]:
                        results.append(result["text"])

            # 获取最终结果
            final_result = json.loads(self.recognizer.FinalResult())
            if "text" in final_result and final_result["text"]:
                results.append(final_result["text"])

            # 合并结果
            transcript = " ".join(results)

            # 格式化文本
            if transcript:
                # 首字母大写
                if len(transcript) > 0:
                    transcript = transcript[0].upper() + transcript[1:]
                # 如果文本末尾没有标点符号，添加句号
                if transcript[-1] not in ['.', '?', '!', ',', ';', ':', '-']:
                    transcript += '.'

            logger.info(f"文件转录完成，长度: {len(transcript)} 字符")
            return transcript if transcript else None

        except Exception as e:
            logger.error(f"转录文件失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None
