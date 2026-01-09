"""非对称加密模块

提供 RSA 加密解密功能
"""

import re
import base64
import binascii
from textwrap import wrap

from loguru import logger
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, PKCS1_OAEP
from Crypto.Hash import SHA1, SHA224, SHA256, SHA384, SHA512, SHA3_224, SHA3_256, SHA3_384, SHA3_512

RSA_HASH_MAP = {
    "SHA1": SHA1,
    "SHA224": SHA224,
    "SHA256": SHA256,
    "SHA384": SHA384,
    "SHA512": SHA512,
    "SHA3_224": SHA3_224,
    "SHA3_256": SHA3_256,
    "SHA3_384": SHA3_384,
    "SHA3_512": SHA3_512,
}


def _to_standard_pem(key_pem: str | bytes) -> str | bytes:
    """将公钥或私钥转换为标准 PEM 格式

    Args:
        key_pem: 公钥或私钥字符串或字节数据

    Returns:
        标准格式的 PEM 公钥或私钥
    """
    try:
        input_is_bytes = isinstance(key_pem, (bytes, bytearray))
        if input_is_bytes:
            key_pem = key_pem.decode("utf-8", errors="ignore")
        key_type = None
        for candidate in ("RSA PRIVATE KEY", "PRIVATE KEY", "PUBLIC KEY"):
            if re.search(rf"-----BEGIN {candidate}-----.+-----END {candidate}-----", key_pem, re.DOTALL):
                key_type = candidate
                break
        if key_type:
            match = re.search(rf"-----BEGIN {key_type}-----(.+?)-----END {key_type}-----", key_pem, re.DOTALL)
            base64_content = match.group(1)
            base64_content = re.sub(r"\s", "", base64_content)
            base64_content = base64_content.replace("-", "+").replace("_", "/")
            padding_length = 4 - (len(base64_content) % 4)
            if padding_length != 4:
                base64_content += "=" * padding_length
            decoded_content = base64.b64decode(base64_content)
            standard_base64 = base64.b64encode(decoded_content).decode("ascii")
        else:
            clean_key = re.sub(r"[^A-Za-z0-9+/=_-]", "", key_pem)
            clean_key = clean_key.replace("-", "+").replace("_", "/")
            padding_length = 4 - (len(clean_key) % 4)
            if padding_length != 4:
                clean_key += "=" * padding_length
            decoded_content = base64.b64decode(clean_key)
            standard_base64 = base64.b64encode(decoded_content).decode("ascii")
            key_type = "PUBLIC KEY"
        formatted_base64 = wrap(standard_base64, 64)
        pem_text = "-----BEGIN {}-----\n{}\n-----END {}-----".format(key_type, "\n".join(formatted_base64), key_type)
        return pem_text.encode("ascii") if input_is_bytes else pem_text
    except Exception:
        logger.exception("密钥格式转换失败")
        raise ValueError("密钥格式无效")


def generate_rsa_keypair(key_size: int = 2048) -> tuple[bytes, bytes]:
    """生成 RSA 密钥对

    Args:
        key_size: 密钥长度, 默认 2048 位

    Returns:
        公钥和私钥的字节数据
    """
    try:
        rsa_key = RSA.generate(key_size)
        public_key_bytes = rsa_key.public_key().export_key()
        private_key_bytes = rsa_key.export_key()
        logger.info(f"成功生成 {key_size} 位 RSA 密钥对")
        return public_key_bytes, private_key_bytes
    except Exception:
        logger.exception("RSA 密钥对生成失败")
        raise


def rsa_encrypt(plaintext: str, public_key: str | bytes, mode: str, hash_algorithm: str = "SHA1", output_format: str = "base64") -> str:
    """RSA 加密

    Args:
        plaintext: 待加密的明文
        public_key: 公钥
        mode: 加密模式, 支持 OAEP 和 V1_5
        hash_algorithm: 哈希算法, 默认 SHA1
        output_format: 输出格式, 支持 base64 和 hex

    Returns:
        加密后的密文
    """
    try:
        hash_class = RSA_HASH_MAP[hash_algorithm.upper()]
        standard_pem = _to_standard_pem(public_key)
        rsa_key = RSA.import_key(standard_pem)
        mode = mode.upper()
        if mode == "OAEP":
            cipher = PKCS1_OAEP.new(rsa_key, hashAlgo=hash_class)
        elif mode == "V1_5":
            cipher = PKCS1_v1_5.new(rsa_key)
        else:
            raise ValueError(f"不支持的加密模式: {mode}")
        encrypted_bytes = cipher.encrypt(plaintext.encode("utf-8"))
        result_bytes = binascii.hexlify(encrypted_bytes) if output_format == "hex" else base64.b64encode(encrypted_bytes)
        return result_bytes.decode("utf-8")
    except Exception:
        logger.exception("RSA 加密失败")
        raise


def rsa_encrypt_long(plaintext: str, public_key: str | bytes, mode: str, hash_algorithm: str = "SHA1", output_format: str = "base64") -> str:
    """RSA 长文本分块加密

    Args:
        plaintext: 待加密的明文
        public_key: 公钥
        mode: 加密模式, 支持 OAEP 和 V1_5
        hash_algorithm: 哈希算法, 默认 SHA1
        output_format: 输出格式, 支持 base64 和 hex

    Returns:
        加密后的密文
    """
    try:
        hash_class = RSA_HASH_MAP[hash_algorithm.upper()]
        standard_pem = _to_standard_pem(public_key)
        rsa_key = RSA.import_key(standard_pem)

        plaintext_bytes = plaintext.encode("utf-8")
        encrypted_chunks = b""

        mode = mode.upper()
        if mode == "OAEP":
            cipher = PKCS1_OAEP.new(rsa_key, hashAlgo=hash_class)
            max_block_size = rsa_key.size_in_bytes() - 2 * hash_class.digest_size - 2
        elif mode == "V1_5":
            cipher = PKCS1_v1_5.new(rsa_key)
            max_block_size = rsa_key.size_in_bytes() - 11
        else:
            raise ValueError(f"不支持的加密模式: {mode}")

        for start_index in range(0, len(plaintext_bytes), max_block_size):
            data_block = plaintext_bytes[start_index : start_index + max_block_size]
            encrypted_chunks += cipher.encrypt(data_block)

        result_bytes = binascii.hexlify(encrypted_chunks) if output_format == "hex" else base64.b64encode(encrypted_chunks)
        return result_bytes.decode("utf-8")
    except Exception:
        logger.exception("RSA 长文本加密失败")
        raise


def rsa_decrypt(ciphertext: str, private_key: str | bytes, mode: str, hash_algorithm: str = "SHA1") -> str:
    """RSA 解密

    Args:
        ciphertext: 待解密的密文
        private_key: 私钥
        mode: 解密模式, 支持 OAEP 和 V1_5
        hash_algorithm: 哈希算法, 默认 SHA1

    Returns:
        解密后的明文
    """
    try:
        try:
            encrypted_bytes = binascii.unhexlify(ciphertext)
        except Exception:
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext)
        hash_class = RSA_HASH_MAP[hash_algorithm.upper()]
        standard_pem = _to_standard_pem(private_key)
        rsa_key = RSA.import_key(standard_pem)
        mode = mode.upper()
        if mode == "OAEP":
            cipher = PKCS1_OAEP.new(rsa_key, hashAlgo=hash_class)
            decrypted_bytes = cipher.decrypt(encrypted_bytes)
        elif mode == "V1_5":
            cipher = PKCS1_v1_5.new(rsa_key)
            decrypted_bytes = cipher.decrypt(encrypted_bytes, None)
        else:
            raise ValueError(f"不支持的解密模式: {mode}")
        return decrypted_bytes.decode("utf-8")
    except Exception:
        logger.exception("RSA 解密失败")
        raise


def rsa_algorithm(plaintext: str, exponent: int, modulus: int) -> str:
    """RSA 算法直接计算

    Args:
        plaintext: 待加密的明文
        exponent: 指数
        modulus: 模数

    Returns:
        加密结果的十六进制字符串
    """
    try:
        hex_representation = binascii.hexlify(plaintext.encode("utf-8")).decode("utf-8")
        encrypted_number = int(hex_representation, 16) ** exponent % modulus
        return hex(encrypted_number)[2:]
    except Exception:
        logger.exception("RSA 算法计算失败")
        raise
