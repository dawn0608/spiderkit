"""通用工具函数模块

提供 JSON 序列化, 键名转换, Cookies 解析等常用工具函数
"""

import json

import inflection
from loguru import logger


def to_json(data: dict, indent: int = 2) -> str:
    """将字典数据转换为格式化的 JSON 字符串

    Args:
        data: 要转换的字典
        indent: 缩进空格数

    Returns:
        格式化后的 JSON 字符串
    """
    try:
        return json.dumps(data, ensure_ascii=False, indent=indent)
    except Exception:
        logger.exception("JSON 序列化失败")
        raise


def convert_keys_to_snake_case(obj: dict | list) -> dict | list:
    """递归将对象中的键名转换为 snake_case 格式

    Args:
        obj: 要转换的字典或列表

    Returns:
        键名转换为 snake_case 格式后的对象
    """
    if isinstance(obj, dict):
        return {(inflection.underscore(key) if isinstance(key, str) else key): convert_keys_to_snake_case(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_keys_to_snake_case(item) for item in obj]
    return obj


def parse_cookies(cookies_input: dict | str) -> dict[str, str]:
    """解析 cookies 输入, 支持字典或字符串格式

    Args:
        cookies_input: cookies 输入, 可以是字典或字符串

    Returns:
        解析后的 cookies 字典
    """
    try:
        if isinstance(cookies_input, dict):
            return {str(key): str(value) for key, value in cookies_input.items()}
        if not isinstance(cookies_input, str):
            raise TypeError(f"cookies_input 必须是 dict 或 str, 当前类型为: {type(cookies_input).__name__}")
        cookies_str = cookies_input.strip()
        if not cookies_str:
            return {}
        cookies_dict: dict[str, str] = {}
        for part in cookies_str.split(";"):
            part = part.strip()
            if not part or "=" not in part:
                continue
            key, value = part.split("=", 1)
            cookies_dict[key.strip()] = value.strip()
        return cookies_dict
    except Exception:
        logger.exception("解析 cookies 失败")
        raise
