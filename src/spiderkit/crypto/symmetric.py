"""对称加密模块

提供 AES、DES、3DES 加密解密功能
"""

import base64
import hashlib
import binascii

from loguru import logger
from Crypto.Cipher import AES, DES, DES3
from Crypto.Util.Padding import pad, unpad


def _get_key_iv_bytes(encryption_key: str | bytes, iv: str | bytes | None = None, encoding_method: str | None = None) -> tuple[bytes, bytes | None]:
    """处理密钥和初始化向量的编码

    Args:
        encryption_key: 加密密钥
        iv: 初始化向量
        encoding_method: 编码方法, 支持 md5, base64, hex

    Returns:
        处理后的密钥和初始化向量
    """
    try:
        method = encoding_method.lower() if encoding_method else None
        if method:
            encoding_methods = {
                "md5": lambda data: hashlib.md5(data.encode("utf-8")).digest(),
                "base64": lambda data: base64.urlsafe_b64decode(data),
                "hex": lambda data: bytes.fromhex(data),
            }
            encoder_function = encoding_methods.get(method)
            if not encoder_function:
                raise ValueError(f"不支持的编码方法: {encoding_method}")
            processed_key = encoder_function(encryption_key)
            processed_iv = encoder_function(iv) if iv is not None else None
        else:
            processed_key = encryption_key.encode("utf-8") if isinstance(encryption_key, str) else encryption_key
            processed_iv = iv.encode("utf-8") if isinstance(iv, str) and iv is not None else iv
        return processed_key, processed_iv
    except Exception:
        logger.exception("密钥和初始化向量编码处理失败")
        raise


def aes_encrypt(plaintext: str, encryption_key: str | bytes, mode: str, iv: str | bytes | None = None, encoding_method: str | None = None, output_format: str = "base64") -> str:
    """AES 加密

    Args:
        plaintext: 待加密的明文
        encryption_key: 加密密钥
        mode: 加密模式, 支持 ECB 和 CBC
        iv: 初始化向量, CBC 模式必需
        encoding_method: 密钥编码方法, 支持 md5, base64, hex
        output_format: 输出格式, 支持 base64 和 hex

    Returns:
        加密后的密文
    """
    try:
        key_bytes, iv_bytes = _get_key_iv_bytes(encryption_key, iv, encoding_method)
        mode = mode.upper()
        if mode == "ECB":
            cipher = AES.new(key=key_bytes, mode=AES.MODE_ECB)
        elif mode == "CBC":
            cipher = AES.new(key=key_bytes, mode=AES.MODE_CBC, iv=iv_bytes)
        else:
            raise ValueError("加密模式必须是 ECB 或 CBC")
        padded_plaintext = pad(plaintext.encode("utf-8"), AES.block_size)
        encrypted_bytes = cipher.encrypt(padded_plaintext)
        result_bytes = binascii.hexlify(encrypted_bytes) if output_format == "hex" else base64.b64encode(encrypted_bytes)
        return result_bytes.decode("utf-8")
    except Exception:
        logger.exception("AES 加密失败")
        raise


def aes_decrypt(ciphertext: str, encryption_key: str | bytes, mode: str, iv: str | bytes | None = None, encoding_method: str | None = None) -> str:
    """AES 解密

    Args:
        ciphertext: 待解密的密文
        encryption_key: 加密密钥
        mode: 解密模式, 支持 ECB 和 CBC
        iv: 初始化向量, CBC 模式必需
        encoding_method: 密钥编码方法

    Returns:
        解密后的明文
    """
    try:
        try:
            encrypted_data = binascii.unhexlify(ciphertext)
        except Exception:
            encrypted_data = base64.urlsafe_b64decode(ciphertext)
        key_bytes, iv_bytes = _get_key_iv_bytes(encryption_key, iv, encoding_method)
        mode = mode.upper()
        if mode == "ECB":
            cipher = AES.new(key=key_bytes, mode=AES.MODE_ECB)
        elif mode == "CBC":
            cipher = AES.new(key=key_bytes, mode=AES.MODE_CBC, iv=iv_bytes)
        else:
            raise ValueError("解密模式必须是 ECB 或 CBC")
        decrypted_bytes = cipher.decrypt(encrypted_data)
        unpadded_plaintext = unpad(decrypted_bytes, AES.block_size)
        return unpadded_plaintext.decode("utf-8")
    except Exception:
        logger.exception("AES 解密失败")
        raise


def des_encrypt(plaintext: str, encryption_key: str | bytes, mode: str, iv: str | bytes | None = None, encoding_method: str | None = None, output_format: str = "base64") -> str:
    """DES 加密

    Args:
        plaintext: 待加密的明文
        encryption_key: 加密密钥
        mode: 加密模式, 支持 ECB 和 CBC
        iv: 初始化向量, CBC 模式必需
        encoding_method: 密钥编码方法
        output_format: 输出格式, 支持 base64 和 hex

    Returns:
        加密后的密文
    """
    try:
        key_bytes, iv_bytes = _get_key_iv_bytes(encryption_key, iv, encoding_method)
        mode = mode.upper()
        if mode == "ECB":
            cipher = DES.new(key=key_bytes, mode=DES.MODE_ECB)
        elif mode == "CBC":
            cipher = DES.new(key=key_bytes, mode=DES.MODE_CBC, iv=iv_bytes)
        else:
            raise ValueError("加密模式必须是 ECB 或 CBC")
        padded_plaintext = pad(plaintext.encode("utf-8"), DES.block_size)
        encrypted_bytes = cipher.encrypt(padded_plaintext)
        result_bytes = binascii.hexlify(encrypted_bytes) if output_format == "hex" else base64.b64encode(encrypted_bytes)
        return result_bytes.decode("utf-8")
    except Exception:
        logger.exception("DES 加密失败")
        raise


def des_decrypt(ciphertext: str, encryption_key: str | bytes, mode: str, iv: str | bytes | None = None, encoding_method: str | None = None) -> str:
    """DES 解密

    Args:
        ciphertext: 待解密的密文
        encryption_key: 加密密钥
        mode: 解密模式, 支持 ECB 和 CBC
        iv: 初始化向量, CBC 模式必需
        encoding_method: 密钥编码方法

    Returns:
        解密后的明文
    """
    try:
        try:
            encrypted_data = binascii.unhexlify(ciphertext)
        except Exception:
            encrypted_data = base64.urlsafe_b64decode(ciphertext)
        key_bytes, iv_bytes = _get_key_iv_bytes(encryption_key, iv, encoding_method)
        mode = mode.upper()
        if mode == "ECB":
            cipher = DES.new(key=key_bytes, mode=DES.MODE_ECB)
        elif mode == "CBC":
            cipher = DES.new(key=key_bytes, mode=DES.MODE_CBC, iv=iv_bytes)
        else:
            raise ValueError("解密模式必须是 ECB 或 CBC")
        decrypted_bytes = cipher.decrypt(encrypted_data)
        unpadded_plaintext = unpad(decrypted_bytes, DES.block_size)
        return unpadded_plaintext.decode("utf-8")
    except Exception:
        logger.exception("DES 解密失败")
        raise


def des3_encrypt(plaintext: str, encryption_key: str | bytes, mode: str, iv: str | bytes | None = None, encoding_method: str | None = None, output_format: str = "base64") -> str:
    """3DES 加密

    Args:
        plaintext: 待加密的明文
        encryption_key: 加密密钥
        mode: 加密模式, 支持 ECB 和 CBC
        iv: 初始化向量, CBC 模式必需
        encoding_method: 密钥编码方法
        output_format: 输出格式, 支持 base64 和 hex

    Returns:
        加密后的密文
    """
    try:
        key_bytes, iv_bytes = _get_key_iv_bytes(encryption_key, iv, encoding_method)
        mode = mode.upper()
        if mode == "ECB":
            cipher = DES3.new(key=key_bytes, mode=DES3.MODE_ECB)
        elif mode == "CBC":
            cipher = DES3.new(key=key_bytes, mode=DES3.MODE_CBC, iv=iv_bytes)
        else:
            raise ValueError("加密模式必须是 ECB 或 CBC")
        padded_plaintext = pad(plaintext.encode("utf-8"), DES3.block_size)
        encrypted_bytes = cipher.encrypt(padded_plaintext)
        result_bytes = binascii.hexlify(encrypted_bytes) if output_format == "hex" else base64.b64encode(encrypted_bytes)
        return result_bytes.decode("utf-8")
    except Exception:
        logger.exception("3DES 加密失败")
        raise


def des3_decrypt(ciphertext: str, encryption_key: str | bytes, mode: str, iv: str | bytes | None = None, encoding_method: str | None = None) -> str:
    """3DES 解密

    Args:
        ciphertext: 待解密的密文
        encryption_key: 加密密钥
        mode: 解密模式, 支持 ECB 和 CBC
        iv: 初始化向量, CBC 模式必需
        encoding_method: 密钥编码方法

    Returns:
        解密后的明文
    """
    try:
        try:
            encrypted_data = binascii.unhexlify(ciphertext)
        except Exception:
            encrypted_data = base64.urlsafe_b64decode(ciphertext)
        key_bytes, iv_bytes = _get_key_iv_bytes(encryption_key, iv, encoding_method)
        mode = mode.upper()
        if mode == "ECB":
            cipher = DES3.new(key=key_bytes, mode=DES3.MODE_ECB)
        elif mode == "CBC":
            cipher = DES3.new(key=key_bytes, mode=DES3.MODE_CBC, iv=iv_bytes)
        else:
            raise ValueError("解密模式必须是 ECB 或 CBC")
        decrypted_bytes = cipher.decrypt(encrypted_data)
        unpadded_plaintext = unpad(decrypted_bytes, DES3.block_size)
        return unpadded_plaintext.decode("utf-8")
    except Exception:
        logger.exception("3DES 解密失败")
        raise
