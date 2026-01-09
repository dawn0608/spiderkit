"""哈希工具模块

提供常用的哈希函数实现
"""

import base64
import hashlib
from typing import Callable

from loguru import logger


def _hash_text(algorithm: Callable[[], "hashlib._Hash"], text: str, output_format: str, error_label: str) -> str | bytes:
    """计算文本的哈希值

    Args:
        algorithm: 哈希算法函数
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64
        error_label: 错误标签, 用于日志记录

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    try:
        fmt = output_format.lower()
        hasher = algorithm()
        hasher.update(text.encode("utf-8"))
        format_handlers = {
            "hex": lambda h: h.hexdigest(),
            "binary": lambda h: h.digest(),
            "base64": lambda h: base64.b64encode(h.digest()).decode("utf-8"),
        }
        handler = format_handlers.get(fmt)
        if not handler:
            raise ValueError(f"不支持的输出格式: {output_format}")
        return handler(hasher)
    except Exception:
        logger.exception(f"{error_label} 哈希计算失败")
        raise


def md5(text: str, output_format: str = "hex") -> str | bytes:
    """计算文本的 MD5 哈希值

    Args:
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    return _hash_text(hashlib.md5, text, output_format, "MD5")


def sha1(text: str, output_format: str = "hex") -> str | bytes:
    """计算文本的 SHA1 哈希值

    Args:
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    return _hash_text(hashlib.sha1, text, output_format, "SHA1")


def sha224(text: str, output_format: str = "hex") -> str | bytes:
    """计算文本的 SHA224 哈希值

    Args:
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    return _hash_text(hashlib.sha224, text, output_format, "SHA224")


def sha256(text: str, output_format: str = "hex") -> str | bytes:
    """计算文本的 SHA256 哈希值

    Args:
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    return _hash_text(hashlib.sha256, text, output_format, "SHA256")


def sha384(text: str, output_format: str = "hex") -> str | bytes:
    """计算文本的 SHA384 哈希值

    Args:
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    return _hash_text(hashlib.sha384, text, output_format, "SHA384")


def sha512(text: str, output_format: str = "hex") -> str | bytes:
    """计算文本的 SHA512 哈希值

    Args:
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    return _hash_text(hashlib.sha512, text, output_format, "SHA512")


def sha3_256(text: str, output_format: str = "hex") -> str | bytes:
    """计算文本的 SHA3-256 哈希值

    Args:
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    return _hash_text(hashlib.sha3_256, text, output_format, "SHA3-256")


def blake2b(text: str, output_format: str = "hex") -> str | bytes:
    """计算文本的 BLAKE2b 哈希值

    Args:
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    return _hash_text(hashlib.blake2b, text, output_format, "BLAKE2b")


def blake2s(text: str, output_format: str = "hex") -> str | bytes:
    """计算文本的 BLAKE2s 哈希值

    Args:
        text: 待计算哈希的文本
        output_format: 输出格式, 支持 hex, binary, base64

    Returns:
        哈希值, 格式根据 output_format 参数决定
    """
    return _hash_text(hashlib.blake2s, text, output_format, "BLAKE2s")
