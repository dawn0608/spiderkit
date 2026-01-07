"""配置管理模块

提供全局配置管理功能
"""

from .settings import SpiderKitConfig, get_config, set_config

__all__ = ["SpiderKitConfig", "get_config", "set_config"]
