"""Argos translation plugin"""
from ..base.plugin_base import PluginBase

class ArgosPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "argos"
        
    def get_id(self) -> str:
        return "argos_translation"
        
    def get_name(self) -> str:
        return "Argos Translation Plugin"
        
    def get_author(self) -> str:
        return "RTM Team"
        
    def get_description(self) -> str:
        return "Argos Machine Translation Plugin"
        
    def get_version(self) -> str:
        return "1.0.0"
        
    def setup(self) -> bool:
        return True
        
    def teardown(self) -> bool:
        return True
        
    def initialize(self) -> bool:
        return True  # 临时返回True用于测试