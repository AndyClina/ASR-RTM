"""
测试配置管理器
"""
import os
import sys
import json
import shutil
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入配置管理器
from src.utils.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """测试配置管理器类"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建测试配置目录
        self.test_config_dir = os.path.join(project_root, 'tests', 'test_config')
        os.makedirs(self.test_config_dir, exist_ok=True)

        # 创建测试配置文件
        self.test_config_path = os.path.join(self.test_config_dir, 'config.json')
        self.test_models_path = os.path.join(self.test_config_dir, 'models.json')
        self.test_plugins_path = os.path.join(self.test_config_dir, 'plugins.json')

        # 创建测试配置
        self.test_config = {
            "version": "2.0.0",
            "app": {
                "name": "测试应用",
                "default_file": ""
            },
            "paths": {
                "models_base": os.path.join(self.test_config_dir, 'models'),
                "models_config": self.test_models_path,
                "plugins_config": self.test_plugins_path,
                "logs_dir": os.path.join(self.test_config_dir, 'logs')
            },
            "asr": {
                "default_model": "test_model",
                "models": {
                    "test_model": {
                        "name": "测试模型",
                        "path": "asr/test/model",
                        "type": "standard",
                        "config": {
                            "sample_rate": 16000,
                            "use_words": True
                        }
                    }
                }
            },
            "transcription": {
                "default_model": "test_model",
                "chunk_size": 0.5,
                "sample_rate": 16000
            }
        }

        # 创建测试模型配置
        self.test_models = {
            "asr": {
                "test_model": {
                    "path": "asr/test/model",
                    "type": "standard",
                    "enabled": True,
                    "config": {
                        "sample_rate": 16000,
                        "use_words": True
                    }
                }
            }
        }

        # 创建测试插件配置
        self.test_plugins = {
            "version": "1.0.0",
            "plugins": {
                "asr": {
                    "test_plugin": {
                        "enabled": True,
                        "type": "asr",
                        "model_config": "test_model",
                        "plugin_config": {
                            "use_words": True
                        }
                    }
                }
            }
        }

        # 写入测试配置文件
        with open(self.test_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_config, f, indent=4, ensure_ascii=False)

        with open(self.test_models_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_models, f, indent=4, ensure_ascii=False)

        with open(self.test_plugins_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_plugins, f, indent=4, ensure_ascii=False)

        # 创建配置管理器实例
        self.config_manager = ConfigManager()

        # 保存原始配置路径
        self._original_config_path = self.config_manager._config_path
        self._original_plugins_path = self.config_manager._plugins_path

        # 设置测试配置路径
        self.config_manager._config_path = self.test_config_path
        self.config_manager._plugins_path = self.test_plugins_path

    def test_load_config(self):
        """测试加载配置"""
        # 加载配置
        config = self.config_manager.load_config()

        # 验证配置
        self.assertIsNotNone(config)
        self.assertEqual(config.get('version'), "2.0.0")
        self.assertEqual(config.get('app', {}).get('name'), "测试应用")

        # 验证 ASR 配置
        asr = config.get('asr', {})
        self.assertIn('models', asr)
        self.assertIn('default_model', asr)

        # 验证插件配置
        plugins = config.get('plugins', {})
        self.assertIn('version', plugins)
        self.assertIn('plugins', plugins)

    def test_get_config(self):
        """测试获取配置"""
        # 加载配置
        self.config_manager.load_config()

        # 获取配置
        app_name = self.config_manager.get_config('app', 'name')
        default_model = self.config_manager.get_config('transcription', 'default_model')

        # 验证配置
        self.assertEqual(app_name, "测试应用")
        self.assertEqual(default_model, "test_model")

        # 测试点号分隔的键
        app_name_dot = self.config_manager.get_config('app.name')
        self.assertEqual(app_name_dot, "测试应用")

        # 测试默认值
        non_existent = self.config_manager.get_config('non_existent', default='默认值')
        self.assertEqual(non_existent, '默认值')

    def test_set_config(self):
        """测试设置配置"""
        # 加载配置
        self.config_manager.load_config()

        # 设置配置
        self.config_manager.set_config('新应用名称', 'app', 'name')
        self.config_manager.set_config(24000, 'transcription', 'sample_rate')

        # 验证配置
        app_name = self.config_manager.get_config('app', 'name')
        sample_rate = self.config_manager.get_config('transcription', 'sample_rate')

        self.assertEqual(app_name, '新应用名称')
        self.assertEqual(sample_rate, 24000)

        # 测试点号分隔的键
        self.config_manager.set_config('点号应用名称', 'app.name')
        app_name = self.config_manager.get_config('app', 'name')
        self.assertEqual(app_name, '点号应用名称')

        # 测试创建新的嵌套配置
        self.config_manager.set_config('新值', 'new', 'nested', 'key')
        new_value = self.config_manager.get_config('new', 'nested', 'key')
        self.assertEqual(new_value, '新值')

    def test_save_config(self):
        """测试保存配置"""
        # 加载配置
        self.config_manager.load_config()

        # 修改配置
        self.config_manager.set_config('保存测试', 'app', 'name')

        # 保存配置
        result = self.config_manager.save_config()
        self.assertTrue(result)

        # 重新加载配置
        with open(self.test_config_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)

        # 验证配置
        self.assertEqual(saved_config.get('app', {}).get('name'), '保存测试')

    def test_resolve_paths(self):
        """测试路径解析"""
        # 加载配置
        self.config_manager.load_config()

        # 修改模型路径为相对路径
        self.config_manager.set_config('relative/path', 'models', 'asr', 'test_model', 'path')

        # 解析路径
        self.config_manager._resolve_paths()

        # 获取解析后的路径
        model_path = self.config_manager.get_config('models', 'asr', 'test_model', 'path')

        # 验证路径已转换为绝对路径
        self.assertTrue(os.path.isabs(model_path))
        self.assertTrue(model_path.endswith('relative/path'))

    def tearDown(self):
        """测试后的清理工作"""
        # 恢复原始配置路径
        self.config_manager._config_path = self._original_config_path
        self.config_manager._plugins_path = self._original_plugins_path

        # 删除测试配置目录
        if os.path.exists(self.test_config_dir):
            shutil.rmtree(self.test_config_dir)

if __name__ == '__main__':
    unittest.main()
