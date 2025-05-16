"""ASR插件基类模块"""
from typing import Optional, Dict, Any, Union, List
import numpy as np
import logging
from ..base.plugin_base import PluginBase

class ASRPlugin(PluginBase):
    """ASR插件基类，继承自PluginBase"""

    def __init__(self):
        """初始化ASR插件"""
        super().__init__()
        self.model_type = None
        self._recognizer = None
        self.engine_type = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_recognizer(self):
        """创建识别器实例"""
        raise NotImplementedError

    def transcribe(self, audio_data: Union[bytes, np.ndarray]) -> Optional[str]:
        """转录音频数据

        Args:
            audio_data: 音频数据，可以是字节或numpy数组

        Returns:
            str: 转录文本，失败返回None
        """
        raise NotImplementedError

    def transcribe_file(self, file_path: str) -> Optional[str]:
        """转录音频文件

        Args:
            file_path: 音频文件路径

        Returns:
            str: 转录文本，失败返回None
        """
        raise NotImplementedError

    def validate_files(self) -> bool:
        """验证模型文件完整性

        Returns:
            bool: 文件是否完整有效
        """
        raise NotImplementedError

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        raise NotImplementedError

    @property
    def supported_models(self) -> List[str]:
        """支持的模型列表"""
        raise NotImplementedError

    def load_model(self, model_path: str) -> bool:
        """加载模型

        Args:
            model_path: 模型路径

        Returns:
            bool: 是否成功加载
        """
        raise NotImplementedError

    def reset(self) -> None:
        """重置识别器状态"""
        try:
            if self._recognizer is not None and hasattr(self._recognizer, 'Reset'):
                self._recognizer.Reset()
        except AttributeError as e:
            self.logger.debug(f"Reset operation failed: {e}")

    def get_final_result(self) -> Optional[str]:
        """获取最终识别结果"""
        try:
            if self._recognizer and hasattr(self._recognizer, 'FinalResult'):
                result = self._recognizer.FinalResult()
                return str(result) if result is not None else None
            return None
        except AttributeError:
            return None

    def cleanup(self) -> bool:
        """清理资源

        Returns:
            bool: 清理是否成功
        """
        try:
            self.reset()  # 先重置识别器
            self._recognizer = None
            return super().cleanup()  # 调用父类的cleanup方法
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return False