"""插件系统测试模块"""
import sys
import pytest
import logging
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.plugins.base.plugin_base import PluginBase
from src.core.plugins.base.plugin_registry import PluginRegistry
from src.core.plugins.base.plugin_manager import PluginManager

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestPluginBase(PluginBase):
    """测试插件基类"""

    def __init__(self):
        """初始化测试插件"""
        super().__init__()
        self.initialized = False
        self.cleaned_up = False
        self._config = {}

    def initialize(self, config=None):
        """初始化插件"""
        self.initialized = True
        if config:
            self._config = config
        return True

    def cleanup(self):
        """清理插件"""
        self.cleaned_up = True
        return True

    def setup(self):
        """设置插件"""
        return True

    def teardown(self):
        """清理插件"""
        return True

    def get_id(self):
        """获取插件ID"""
        return "test_plugin"

    def get_name(self):
        """获取插件名称"""
        return "Test Plugin"

    def get_version(self):
        """获取插件版本"""
        return "1.0.0"

    def get_description(self):
        """获取插件描述"""
        return "测试插件"

    def get_author(self):
        """获取插件作者"""
        return "Test Author"

@pytest.fixture
def plugin_manager():
    """创建插件管理器实例"""
    return PluginManager()

@pytest.fixture
def plugin_registry(plugin_manager):
    """创建插件注册表实例"""
    return plugin_manager.get_registry()

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """测试配置"""
    return {
        "asr": {
            "models": {
                "vosk_small": {
                    "path": "models/asr/vosk/vosk-model-small-en-us-0.15",
                    "type": "standard",  # 使用与config.json一致的类型
                    "enabled": True,
                    "config": {
                        "sample_rate": 16000,
                        "use_words": True,
                        "channels": 1,
                        "buffer_size": 4000
                    }
                }
            }
        }
    }

def test_plugin_loading(plugin_registry):
    """测试插件加载"""
    # 注册测试插件
    plugin_registry.register("test_plugin", TestPluginBase)

    # 加载插件
    result = plugin_registry.load_plugin("test_plugin")

    # 验证是否成功加载了插件
    assert result is True
    assert plugin_registry.is_loaded("test_plugin") is True

    # 获取插件实例
    plugin = plugin_registry.get_plugin("test_plugin")
    assert plugin is not None
    assert isinstance(plugin, TestPluginBase)
    assert hasattr(plugin, "initialized")
    assert plugin.initialized is True

def test_plugin_registry():
    """测试插件注册表"""
    # 创建插件注册表
    registry = PluginRegistry()

    # 注册测试插件
    result = registry.register("test_plugin", TestPluginBase)
    assert result is True
    assert registry.is_registered("test_plugin") is True

    # 加载测试插件
    result = registry.load_plugin("test_plugin", {"test": "value"})
    assert result is True
    assert registry.is_loaded("test_plugin") is True

    # 获取测试插件
    plugin = registry.get_plugin("test_plugin")
    assert plugin is not None
    assert isinstance(plugin, TestPluginBase)
    assert hasattr(plugin, "initialized")
    assert plugin.initialized is True
    assert hasattr(plugin, "_config")
    assert plugin._config == {"test": "value"}

    # 卸载测试插件
    result = registry.unload_plugin("test_plugin")
    assert result is True
    assert registry.is_loaded("test_plugin") is False

if __name__ == "__main__":
    pytest.main(["-v", __file__])