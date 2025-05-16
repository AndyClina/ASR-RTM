"""
测试 VoskPlugin 插件
"""
import os
import sys
import logging
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入 VoskPlugin
from src.core.plugins.asr.vosk_plugin.vosk_plugin import VoskPlugin

class TestVoskPlugin(unittest.TestCase):
    """测试 VoskPlugin 类"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建 VoskPlugin 实例
        self.plugin = VoskPlugin()
        
        # 设置测试配置
        self.config = {
            "path": "C:\\Users\\crige\\models\\asr\\vosk\\vosk-model-small-en-us-0.15",
            "sample_rate": 16000,
            "use_words": True
        }

    def test_initialization(self):
        """测试插件初始化"""
        # 初始化插件
        success = self.plugin.initialize(self.config)
        self.assertTrue(success, "插件初始化失败")
        self.assertEqual(self.plugin.engine_type, "vosk_small", "引擎类型不正确")
        
    def test_get_info(self):
        """测试获取插件信息"""
        # 初始化插件
        self.plugin.initialize(self.config)
        
        # 获取插件信息
        plugin_id = self.plugin.get_id()
        plugin_name = self.plugin.get_name()
        plugin_version = self.plugin.get_version()
        plugin_description = self.plugin.get_description()
        plugin_author = self.plugin.get_author()
        
        self.assertEqual(plugin_id, "vosk_small", "插件ID不正确")
        self.assertEqual(plugin_name, "Vosk Small Model", "插件名称不正确")
        self.assertEqual(plugin_version, "1.0.0", "插件版本不正确")
        self.assertTrue(plugin_description, "插件描述为空")
        self.assertTrue(plugin_author, "插件作者为空")
        
    def test_model_info(self):
        """测试获取模型信息"""
        # 初始化插件
        self.plugin.initialize(self.config)
        
        # 获取模型信息
        model_info = self.plugin.get_model_info()
        
        self.assertTrue(model_info, "模型信息为空")
        self.assertEqual(model_info["type"], "vosk_small", "模型类型不正确")
        self.assertEqual(model_info["engine"], "vosk_small", "引擎类型不正确")
        self.assertEqual(model_info["language"], "en", "语言不正确")
        
    def test_supported_models(self):
        """测试支持的模型列表"""
        # 获取支持的模型列表
        supported_models = self.plugin.supported_models
        
        self.assertTrue(supported_models, "支持的模型列表为空")
        self.assertIn("vosk_small", supported_models, "支持的模型列表中缺少 vosk_small")
        
    def test_validate_files(self):
        """测试验证模型文件"""
        # 初始化插件
        self.plugin.initialize(self.config)
        
        # 验证模型文件
        valid = self.plugin.validate_files()
        
        self.assertTrue(valid, "模型文件验证失败")
        
    def test_create_recognizer(self):
        """测试创建识别器"""
        # 初始化插件
        self.plugin.initialize(self.config)
        
        # 创建识别器
        recognizer = self.plugin.create_recognizer()
        
        self.assertIsNotNone(recognizer, "创建识别器失败")
        
    def test_cleanup(self):
        """测试清理资源"""
        # 初始化插件
        self.plugin.initialize(self.config)
        
        # 清理资源
        success = self.plugin.cleanup()
        
        self.assertTrue(success, "清理资源失败")
        self.assertIsNone(self.plugin.model, "清理后模型不为空")
        self.assertIsNone(self.plugin.recognizer, "清理后识别器不为空")
        
    def tearDown(self):
        """测试后的清理工作"""
        # 清理资源
        if hasattr(self, 'plugin') and self.plugin:
            self.plugin.cleanup()

if __name__ == '__main__':
    unittest.main()
