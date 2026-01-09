"""全局配置管理

提供 SpiderKit 的全局配置管理功能
"""

from dataclasses import dataclass, field

from loguru import logger


@dataclass
class SpiderKitConfig:
    """SpiderKit 全局配置类"""

    downloader_concurrency: int = 16
    downloader_timeout: int = 10
    downloader_max_retries: int = 3
    downloader_retry_delay: float = 1.0
    downloader_headers: dict[str, str] = field(default_factory=dict)
    font_image_size: int = 400
    font_size: int = 240
    font_background: tuple = (255, 255, 255, 255)
    font_color: tuple = (0, 0, 0, 255)
    font_include_unicode_escape: bool = False
    font_download_timeout: int = 15
    storage_default_format: str = "csv"
    storage_default_dir: str = "./data"
    storage_default_mode: str = "a"
    log_level: str = "INFO"
    log_format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    temp_dir: str | None = None
    cleanup_temp_files: bool = True


_global_config: SpiderKitConfig | None = None


def _load_config_from_env(config: SpiderKitConfig) -> None:
    """从环境变量加载配置

    Args:
        config: 配置实例
    """
    try:
        import os

        env_mappings = {
            "SPIDERKIT_DOWNLOADER_CONCURRENCY": ("downloader_concurrency", int),
            "SPIDERKIT_DOWNLOADER_TIMEOUT": ("downloader_timeout", int),
            "SPIDERKIT_DOWNLOADER_MAX_RETRIES": ("downloader_max_retries", int),
            "SPIDERKIT_DOWNLOADER_RETRY_DELAY": ("downloader_retry_delay", float),
            "SPIDERKIT_FONT_IMAGE_SIZE": ("font_image_size", int),
            "SPIDERKIT_FONT_SIZE": ("font_size", int),
            "SPIDERKIT_FONT_DOWNLOAD_TIMEOUT": ("font_download_timeout", int),
            "SPIDERKIT_STORAGE_DEFAULT_FORMAT": ("storage_default_format", str),
            "SPIDERKIT_STORAGE_DEFAULT_DIR": ("storage_default_dir", str),
            "SPIDERKIT_STORAGE_DEFAULT_MODE": ("storage_default_mode", str),
            "SPIDERKIT_LOG_LEVEL": ("log_level", str),
            "SPIDERKIT_TEMP_DIR": ("temp_dir", str),
            "SPIDERKIT_CLEANUP_TEMP_FILES": ("cleanup_temp_files", lambda x: x.lower() in ("true", "1", "yes")),
        }
        for env_key, (attr_name, converter) in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                try:
                    converted_value = converter(env_value)
                    setattr(config, attr_name, converted_value)
                    logger.debug(f"从环境变量加载配置: {attr_name} = {converted_value}")
                except Exception:
                    logger.warning(f"环境变量 {env_key} 值无效: {env_value}")
    except Exception:
        logger.exception("从环境变量加载配置失败")
        raise


def get_config() -> SpiderKitConfig:
    """获取全局配置实例

    Returns:
        全局配置实例
    """
    global _global_config
    try:
        if _global_config is None:
            _global_config = SpiderKitConfig()
            _load_config_from_env(_global_config)
            logger.debug("初始化全局配置")
        return _global_config
    except Exception:
        logger.exception("获取全局配置失败")
        raise


def set_config(config: SpiderKitConfig) -> None:
    """设置全局配置实例

    Args:
        config: 新的配置实例
    """
    global _global_config
    try:
        _global_config = config
        logger.debug("更新全局配置")
    except Exception:
        logger.exception("设置全局配置失败")
        raise
