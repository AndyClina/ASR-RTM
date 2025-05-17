#!/usr/bin/env python3
"""
配置管理模块
负责加载和管理配置信息，提供统一的配置访问接口
"""
import os
import json
import logging
import shutil
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理类，单例模式"""
    _instance = None
    _config = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化配置管理器"""
        if self._initialized:
            return

        # 配置文件路径
        self._config_path = os.path.join('config', 'config.json')
        self._plugins_path = os.path.join('config', 'plugins.json')
        self._ui_config_path = os.path.join('config', 'ui_config.json')
        self._translation_config_path = os.path.join('config', 'translation_config.json')

        # 不再需要备份目录
        # self._backup_dir = os.path.join('config', 'backups')
        # os.makedirs(self._backup_dir, exist_ok=True)

        # 初始化配置
        self._config = {}
        self._initialized = True

    @property
    def config(self) -> Dict[str, Any]:
        """获取配置"""
        return self._config

    def load_config(self) -> Dict[str, Any]:
        """加载所有配置文件"""
        try:
            # 加载主配置
            if os.path.exists(self._config_path):
                logger.debug(f"尝试加载主配置文件: {self._config_path}")
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.info("主配置文件加载成功")
            else:
                logger.warning(f"主配置文件不存在: {self._config_path}")
                self._config = {}

            # 加载模型配置
            models_path = os.path.join('config', 'models.json')
            if os.path.exists(models_path):
                logger.debug(f"尝试加载模型配置文件: {models_path}")
                with open(models_path, 'r', encoding='utf-8') as f:
                    models_config = json.load(f)
                    # 将模型配置合并到主配置中
                    self._config['models'] = models_config
                logger.info("模型配置文件加载成功")
            else:
                logger.warning(f"模型配置文件不存在: {models_path}")

            # 加载插件配置
            if os.path.exists(self._plugins_path):
                logger.debug(f"尝试加载插件配置文件: {self._plugins_path}")
                with open(self._plugins_path, 'r', encoding='utf-8') as f:
                    self._config['plugins'] = json.load(f)
                logger.info("插件配置文件加载成功")
            else:
                logger.warning(f"插件配置文件不存在: {self._plugins_path}")

            # 加载UI配置（如果存在）
            if os.path.exists(self._ui_config_path):
                logger.debug(f"尝试加载UI配置文件: {self._ui_config_path}")
                with open(self._ui_config_path, 'r', encoding='utf-8') as f:
                    self._config['ui'] = json.load(f)
                logger.info("UI配置文件加载成功")

            # 加载翻译配置（如果存在）
            if os.path.exists(self._translation_config_path):
                logger.debug(f"尝试加载翻译配置文件: {self._translation_config_path}")
                with open(self._translation_config_path, 'r', encoding='utf-8') as f:
                    self._config['translation'] = json.load(f)
                logger.info("翻译配置文件加载成功")

            # 解析和验证路径
            self._resolve_paths()

            # 验证配置
            if not self.validate_config(self._config):
                logger.warning("配置验证失败，使用默认配置")
                self._init_default_config()

            return self._config

        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {str(e)}")
            logger.warning("使用默认配置")
            self._init_default_config()
            return self._config
        except Exception as e:
            logger.error(f"加载配置文件时发生错误: {str(e)}")
            logger.warning("使用默认配置")
            self._init_default_config()
            return self._config

    def _resolve_paths(self):
        """解析和验证配置中的路径"""
        try:
            # 确保 _config 是字典
            if self._config is None:
                self._config = {}

            # 获取基础路径
            paths_dict = self._config.get('paths', {})
            if not isinstance(paths_dict, dict):
                paths_dict = {}

            base_path = paths_dict.get('models_base', '')
            if not base_path:
                logger.warning("配置中缺少模型基础路径，使用当前目录")
                base_path = os.path.abspath('models')
                # 更新配置
                if 'paths' not in self._config:
                    self._config['paths'] = {}
                self._config['paths']['models_base'] = base_path

            # 确保基础路径存在
            os.makedirs(base_path, exist_ok=True)

            # 解析模型路径
            models_dict = self._config.get('models', {})
            if isinstance(models_dict, dict):
                for model_type_key, models_by_type in models_dict.items():
                    if isinstance(models_by_type, dict):
                        for model_name_key, model_config in models_by_type.items():
                            if isinstance(model_config, dict) and 'path' in model_config:
                                path = model_config['path']
                                # 如果是相对路径，转换为绝对路径
                                if not os.path.isabs(path):
                                    abs_path = os.path.join(base_path, path)
                                    logger.info(f"将相对路径 {path} 转换为绝对路径: {abs_path}")
                                    model_config['path'] = abs_path

            logger.info("路径解析完成")
        except Exception as e:
            logger.error(f"解析路径时发生错误: {str(e)}")

    def _init_default_config(self):
        """初始化默认配置"""
        self._config = {
            "version": "2.0.0",
            "app": {
                "name": "实时转录系统",
                "default_file": ""
            },
            "paths": {
                "models_base": os.path.abspath('models'),
                "models_config": "config/models.json",
                "plugins_config": "config/plugins.json",
                "logs_dir": "logs"
            },
            "models": {
                "asr": {
                    "vosk_small": {
                        "path": "asr/vosk/vosk-model-small-en-us-0.15",
                        "type": "standard",
                        "enabled": True,
                        "config": {
                            "sample_rate": 16000,
                            "use_words": True,
                            "channels": 1,
                            "buffer_size": 4000
                        }
                    }
                }
            },
            "transcription": {
                "default_model": "vosk_small",
                "chunk_size": 0.5,
                "tail_padding": 0.2,
                "sample_rate": 16000,
                "language": "en",
                "asr": {
                    "enable_endpoint": True,
                    "rule1_min_trailing_silence": 2.4,
                    "rule2_min_trailing_silence": 1.2,
                    "rule3_min_utterance_length": 20.0
                }
            },
            "window": {
                "title": "实时字幕",
                "pos_x": 100,
                "pos_y": 100,
                "width": 800,
                "height": 400,
                "opacity": 0.9,
                "always_on_top": True,
                "background_mode": "translucent"
            },
            "ui": {
                "theme": "dark",
                "language": "zh_CN",
                "fonts": {
                    "subtitle": {
                        "family": "Arial",
                        "size": 24,
                        "weight": "bold",
                        "color": "#FFFFFF"
                    }
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/app.log"
            }
        }

        # 解析路径
        self._resolve_paths()

        logger.info("已初始化默认配置")

    def save_config(self, section: Optional[str] = None) -> bool:
        """保存配置

        Args:
            section: 要保存的配置部分，None表示保存所有配置

        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保 _config 是字典
            if self._config is None:
                self._config = {}

            # 不再创建备份
            # self._create_backup()

            if section is None or section == 'main':
                # 保存主配置
                main_config = {}
                for k, v in self._config.items():
                    if k not in ['plugins', 'ui', 'translation']:
                        main_config[k] = v

                with open(self._config_path, 'w', encoding='utf-8') as f:
                    json.dump(main_config, f, indent=4, ensure_ascii=False)
                logger.info(f"已保存主配置: {self._config_path}")

            if section is None or section == 'plugins':
                # 保存插件配置
                plugins_config = self._config.get('plugins', {})
                if not isinstance(plugins_config, dict):
                    plugins_config = {}

                with open(self._plugins_path, 'w', encoding='utf-8') as f:
                    json.dump(plugins_config, f, indent=4, ensure_ascii=False)
                logger.info(f"已保存插件配置: {self._plugins_path}")

            if section is None or section == 'ui':
                # 保存UI配置
                ui_config = self._config.get('ui', {})
                if not isinstance(ui_config, dict):
                    ui_config = {}

                with open(self._ui_config_path, 'w', encoding='utf-8') as f:
                    json.dump(ui_config, f, indent=4, ensure_ascii=False)
                logger.info(f"已保存UI配置: {self._ui_config_path}")

            if section is None or section == 'translation':
                # 保存翻译配置
                translation_config = self._config.get('translation', {})
                if not isinstance(translation_config, dict):
                    translation_config = {}

                with open(self._translation_config_path, 'w', encoding='utf-8') as f:
                    json.dump(translation_config, f, indent=4, ensure_ascii=False)
                logger.info(f"已保存翻译配置: {self._translation_config_path}")

            # 保存模型配置
            if section is None or section == 'models':
                models_path = os.path.join('config', 'models.json')
                models_config = self._config.get('models', {})
                if not isinstance(models_config, dict):
                    models_config = {}

                with open(models_path, 'w', encoding='utf-8') as f:
                    json.dump(models_config, f, indent=4, ensure_ascii=False)
                logger.info(f"已保存模型配置: {models_path}")

            return True
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            return False

    def _create_backup(self):
        """创建配置文件备份（已禁用）"""
        # 此方法已禁用，不再创建备份文件
        pass

    def _cleanup_old_backups(self, max_backups: int = 10):
        """清理旧备份文件（已禁用）

        Args:
            max_backups: 每种配置文件保留的最大备份数量
        """
        # 此方法已禁用，不再清理备份文件
        pass

    def get_config(self, *keys, default=None) -> Any:
        """
        获取配置值

        Args:
            *keys: 配置键路径，例如 'asr', 'models', 'vosk_small'
            default: 默认值，如果配置不存在则返回此值

        Returns:
            Any: 配置值或默认值
        """
        if not keys:
            return default

        try:
            # 如果只有一个键且包含点号，按点号分割
            if len(keys) == 1 and isinstance(keys[0], str) and '.' in keys[0]:
                keys = keys[0].split('.')

            value = self._config
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            return value
        except Exception:
            return default

    def set_config(self, value: Any, *keys) -> bool:
        """
        设置配置值

        Args:
            value: 要设置的值
            *keys: 配置键路径

        Returns:
            bool: 设置是否成功
        """
        if not keys:
            return False

        try:
            # 确保 _config 是字典
            if self._config is None:
                self._config = {}

            # 如果只有一个键且包含点号，按点号分割
            if len(keys) == 1 and isinstance(keys[0], str) and '.' in keys[0]:
                keys = keys[0].split('.')

            # 递归创建嵌套字典
            config = self._config
            for key in keys[:-1]:
                if not isinstance(config, dict):
                    config = {}
                if key not in config:
                    config[key] = {}
                elif not isinstance(config[key], dict):
                    config[key] = {}
                config = config[key]

            # 设置最终值
            if not isinstance(config, dict):
                config = {}
                self._config = config  # 重置根配置
            config[keys[-1]] = value
            return True
        except Exception as e:
            logger.error(f"设置配置值失败: {str(e)}")
            return False

    def get_ui_config(self, *keys, default=None) -> Any:
        """
        获取UI配置

        Args:
            *keys: 配置键路径
            default: 默认值，如果配置不存在则返回此值

        Returns:
            Any: 配置值或默认值
        """
        # 构建完整的键路径
        ui_keys = ['ui']
        ui_keys.extend(keys)
        return self.get_config(*ui_keys, default=default)

    def set_ui_config(self, value: Any, *keys) -> bool:
        """
        设置UI配置

        Args:
            value: 要设置的值
            *keys: 配置键路径

        Returns:
            bool: 设置是否成功
        """
        # 构建完整的键路径
        ui_keys = ['ui']
        ui_keys.extend(keys)
        return self.set_config(value, *ui_keys)

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模型的配置

        Args:
            model_name: 模型名称

        Returns:
            Optional[Dict[str, Any]]: 模型配置或None
        """
        return self.get_config('asr', 'models', model_name)

    def get_plugin_config(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定插件的配置

        Args:
            plugin_id: 插件ID

        Returns:
            Optional[Dict[str, Any]]: 插件配置或None
        """
        # 首先尝试从plugins.plugins获取
        plugin_config = self.get_config('plugins', 'plugins', plugin_id)
        if plugin_config:
            return plugin_config

        # 然后尝试从plugins直接获取
        return self.get_config('plugins', plugin_id)

    def get_window_config(self) -> Dict[str, Any]:
        """
        获取窗口配置

        Returns:
            Dict[str, Any]: 窗口配置
        """
        return self.get_config('window', default={})

    def update_window_config(self, config: Dict[str, Any]) -> bool:
        """
        更新窗口配置

        Args:
            config: 新的窗口配置

        Returns:
            bool: 更新是否成功
        """
        if self.set_config(config, 'window'):
            return self.save_config('main')
        return False

    def update_and_save(self, section: str, config: Dict[str, Any]) -> bool:
        """
        更新指定部分的配置并保存

        Args:
            section: 配置部分名称
            config: 新的配置值

        Returns:
            bool: 是否更新成功
        """
        try:
            # 确保 _config 是字典
            if self._config is None:
                self._config = {}

            # 更新配置
            self._config[section] = config

            # 保存配置
            return self.save_config(section)
        except Exception as e:
            logger.error(f"更新并保存配置失败: {str(e)}")
            return False

    def get_default_model(self) -> str:
        """
        获取默认ASR模型名称

        Returns:
            str: 默认模型名称
        """
        # 首先尝试从asr.default_model获取
        default_model = self.get_config('asr', 'default_model')
        if default_model:
            return default_model

        # 然后尝试从transcription.default_model获取
        default_model = self.get_config('transcription', 'default_model')
        if default_model:
            return default_model

        # 最后返回默认值
        return 'vosk_small'

    def validate_model_files(self, model_path: str, model_type: str = "sherpa_onnx") -> bool:
        """
        验证模型文件完整性

        Args:
            model_path: 模型路径
            model_type: 模型类型，支持 "sherpa_onnx" 和 "vosk"

        Returns:
            bool: 验证是否通过
        """
        try:
            if not os.path.exists(model_path):
                logger.error(f"模型路径不存在: {model_path}")
                return False

            if model_type.startswith("sherpa"):
                # Sherpa-ONNX 模型文件验证
                # 注意：这里不是硬编码路径，而是检查必要的文件是否存在
                # 实际文件名可能因模型版本而异，这里只是一个基本检查
                required_files = [
                    "encoder.onnx",
                    "decoder.onnx",
                    "joiner.onnx",
                    "tokens.txt"
                ]

                for file in required_files:
                    file_path = os.path.join(model_path, file)
                    if not os.path.exists(file_path):
                        logger.error(f"缺少Sherpa-ONNX模型文件: {file_path}")
                        return False

            elif model_type == "vosk":
                # Vosk 模型文件验证
                # Vosk 模型只需要检查目录是否存在，以及是否包含 am 和 conf 文件夹
                required_dirs = ["am", "conf"]
                for dir_name in required_dirs:
                    dir_path = os.path.join(model_path, dir_name)
                    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                        logger.error(f"缺少Vosk模型目录: {dir_path}")
                        return False

            else:
                logger.warning(f"未知的模型类型: {model_type}，跳过文件验证")
                return True

            logger.info(f"{model_type}模型文件验证通过: {model_path}")
            return True

        except Exception as e:
            logger.error(f"验证模型文件时发生错误: {str(e)}")
            return False

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置文件的完整性和正确性

        Args:
            config: 配置字典

        Returns:
            bool: 验证是否通过
        """
        # 最小必要配置
        if not config:
            logger.error("配置为空")
            return False

        # 检查必要的顶级键
        required_top_keys = ['app', 'asr']
        for key in required_top_keys:
            if key not in config:
                logger.error(f"缺少必要的配置键: {key}")
                return False

        # 检查ASR配置
        if 'models' not in config.get('asr', {}):
            logger.error("缺少ASR模型配置")
            return False

        # 检查是否至少有一个模型配置
        if not config.get('asr', {}).get('models', {}):
            logger.error("没有配置任何ASR模型")
            return False

        logger.info("配置验证通过")
        return True

    def get_all_config(self) -> Dict[str, Any]:
        """
        获取所有配置

        Returns:
            Dict[str, Any]: 完整的配置字典
        """
        # 确保返回字典
        if self._config is None or not isinstance(self._config, dict):
            return {}
        return self._config

    def get_all_models(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有ASR模型配置

        Returns:
            Dict[str, Dict[str, Any]]: 所有模型配置
        """
        # 首先尝试从 models.asr 获取
        models = self.get_config('models', 'asr', default={})
        if models:
            return models

        # 然后尝试从 asr.models 获取
        models = self.get_config('asr', 'models', default={})
        if models:
            return models

        # 最后尝试直接从 asr 获取
        return self.get_config('asr', default={})

    def get_all_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有插件配置

        Returns:
            Dict[str, Dict[str, Any]]: 所有插件配置
        """
        # 首先尝试从plugins.plugins获取
        plugins = self.get_config('plugins', 'plugins', default={})
        if plugins:
            return plugins

        # 然后尝试从plugins直接获取
        return self.get_config('plugins', default={})

    def register_model(self, model_id: str, model_config: Dict[str, Any]) -> bool:
        """
        注册ASR模型

        Args:
            model_id: 模型ID
            model_config: 模型配置

        Returns:
            bool: 注册是否成功
        """
        if not self.set_config(model_config, 'asr', 'models', model_id):
            return False

        return self.save_config('main')

    def register_plugin(self, plugin_id: str, plugin_config: Dict[str, Any]) -> bool:
        """
        注册插件

        Args:
            plugin_id: 插件ID
            plugin_config: 插件配置

        Returns:
            bool: 注册是否成功
        """
        # 检查plugins.plugins是否存在
        if self.get_config('plugins', 'plugins') is not None:
            if not self.set_config(plugin_config, 'plugins', 'plugins', plugin_id):
                return False
        else:
            if not self.set_config(plugin_config, 'plugins', plugin_id):
                return False

        return self.save_config('plugins')

# 创建全局配置管理器实例
config_manager = ConfigManager()

# 导出
__all__ = [
    'ConfigManager',
    'config_manager'
]
