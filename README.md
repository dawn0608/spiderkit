# SpiderKit

一个面向爬虫与数据处理场景的 Python 工具包，覆盖加密解密、数据存储、异步下载、反爬字体解析与常用哈希工具。

## 功能概览

- **加密解密**: RSA（含长文本分块）、AES/DES/3DES，多种模式与输出格式
- **数据存储**: CSV、JSON、JSONL 格式保存，支持追加写入
- **异步下载**: 高性能并发下载，支持 M3U8 视频分片合并
- **字体解析**: 解析反爬字体文件并生成字符映射
- **哈希工具**: 常用摘要算法与多种输出格式

## 安装

```bash
pip install spiderkit
```

从源码安装：

```bash
pip install -e .
```

## 运行环境

- Python 3.11+
- 可选依赖: `ffmpeg`（M3U8 视频合并与转码需要）

## 模块与核心 API

- `spiderkit.crypto`
  - `generate_rsa_keypair`
  - `rsa_encrypt` / `rsa_encrypt_long` / `rsa_decrypt` / `rsa_algorithm`
  - `aes_encrypt` / `aes_decrypt` / `des_encrypt` / `des_decrypt` / `des3_encrypt` / `des3_decrypt`
- `spiderkit.downloader`
  - `Downloader` / `M3U8Downloader`
- `spiderkit.storage`
  - `save_data_to_file`
- `spiderkit.utils`
  - `parse_font` / `decrypt_text_with_font_maps` / `FontParseConfig`
  - `md5` / `sha1` / `sha224` / `sha256` / `sha384` / `sha512` / `sha3_256`
  - `blake2b` / `blake2s`
- `spiderkit.config`
  - `SpiderKitConfig` / `get_config` / `set_config`

## 快速开始

### 加密解密

```python
import os
from spiderkit.crypto import generate_rsa_keypair, rsa_encrypt, rsa_decrypt, aes_encrypt, aes_decrypt

plaintext = "Hello SpiderKit!"

# RSA 加密解密
public_key, private_key = generate_rsa_keypair()
rsa_encrypted = rsa_encrypt(plaintext, public_key, "OAEP")
print(rsa_encrypted)
rsa_decrypted = rsa_decrypt(rsa_encrypted, private_key, "OAEP")
print(rsa_decrypted)

# AES 加密解密
aes_key = os.urandom(32)
aes_iv = os.urandom(16)
aes_encrypted = aes_encrypt(plaintext, aes_key, "CBC", iv=aes_iv)
print(aes_encrypted)
aes_decrypted = aes_decrypt(aes_encrypted, aes_key, "CBC", iv=aes_iv)
print(aes_decrypted)
```

### 异步下载

```python
from spiderkit.downloader import Downloader, M3U8Downloader

# 可选请求头（部分网站加了防盗链需要 Referer 字段）
headers = {
    "Referer": "https://www.example.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.98 Safari/537.36"
}

# 普通文件下载
downloader = Downloader(headers=headers)
file_mapping = {
    "images/image1.jpg": "https://example.com/image1.jpg",
    "images/image2.jpg": "https://example.com/image2.jpg"
}
downloader.download_files(file_mapping)

# M3U8 视频下载（需安装 ffmpeg）
m3u8_downloader = M3U8Downloader(headers=headers)
m3u8_downloader.download_video("https://example.com/video.m3u8", "output_video.mp4")
```

### 字体解析

```python
from spiderkit.utils import parse_font, decrypt_text_with_font_maps

# 解析字体文件路径或 URL
# font_maps = parse_font("fonts/font.woff")
font_maps = parse_font("https://example.com/font.woff")

# 解密文本
encrypted_text = "加密的文本"
decrypted_text = decrypt_text_with_font_maps(encrypted_text, font_maps)
print(decrypted_text)
```

### 哈希计算

```python
from spiderkit.utils import md5, sha1, sha256, sha512, sha3_256, blake2b

text = "Hello SpiderKit!"

# 默认输出 hex
print(md5(text))
print(sha1(text))
print(sha256(text))
print(sha512(text))

# 其他算法
print(sha3_256(text))
print(blake2b(text))

# 其他输出格式: binary / base64
print(md5(text, "binary"))
print(md5(text, "base64"))
```

### 数据存储

```python
from spiderkit.storage import save_data_to_file

data = [
    {"name": "张三", "age": 25},
    {"name": "李四", "age": 30}
]

# 保存为 CSV
save_data_to_file(data, "users", "csv")

# 保存为 JSON
save_data_to_file(data, "users", "json")

# 保存为 JSONL
save_data_to_file(data, "users", "jsonl")
```

## 使用建议

- `Downloader.download_files` 内部使用 `asyncio.run`，若你已处于事件循环中，请在外部自行编排协程。
- `save_data_to_file` 默认输出目录为 `./data`，写入模式默认 `a`（追加）。

## 配置

SpiderKit 提供统一配置入口，可在运行时调整行为或用环境变量覆盖。

```python
from spiderkit.config import SpiderKitConfig, get_config, set_config

config = get_config()
config.downloader_concurrency = 8
config.storage_default_dir = "./exports"
set_config(config)
```

常用环境变量：

- `SPIDERKIT_DOWNLOADER_CONCURRENCY`
- `SPIDERKIT_DOWNLOADER_TIMEOUT`
- `SPIDERKIT_FONT_SIZE`
- `SPIDERKIT_FONT_DOWNLOAD_TIMEOUT`
- `SPIDERKIT_STORAGE_DEFAULT_DIR`
- `SPIDERKIT_STORAGE_DEFAULT_MODE`
- `SPIDERKIT_LOG_LEVEL`
