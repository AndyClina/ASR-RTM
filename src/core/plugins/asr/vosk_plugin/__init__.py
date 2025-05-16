"""
Vosk插件包
提供Vosk语音识别功能
"""
# 避免重复导入
from .vosk_plugin import VoskPlugin  # type: ignore

# 设置一个标志，表示这个模块已经被导入
__imported__ = True
