# SpiderKit

一个面向爬虫与数据处理场景的 Python 工具包, 覆盖加密解密, 数据存储, 异步下载, 反爬字体解析与常用哈希工具

## 功能概览

- **加密解密**: RSA (含长文本分块), AES/DES/3DES, 多种模式与输出格式
- **数据存储**: CSV, JSON, JSONL 格式保存, 支持追加写入
- **异步下载**: 高性能并发下载, 支持 M3U8 视频分片合并
- **字体解析**: 解析反爬字体文件并生成字符映射
- **哈希工具**: 常用摘要算法与多种输出格式
- **通用工具**: JSON 序列化, 键名转换, Cookies 解析等实用函数

## 安装

```bash
pip install spiderkit
```

从源码安装:

```bash
uv pip install -e .
```

## 运行环境

- Python 3.11+
- 可选依赖: `ffmpeg` (M3U8 视频合并与转码需要)

## 模块与核心 API

- `spiderkit.crypto`
  - `generate_rsa_keypair` - 生成 RSA 密钥对
  - `rsa_encrypt` / `rsa_encrypt_long` / `rsa_decrypt` / `rsa_algorithm` - RSA 加密解密
  - `aes_encrypt` / `aes_decrypt` - AES 加密解密
  - `des_encrypt` / `des_decrypt` - DES 加密解密
  - `des3_encrypt` / `des3_decrypt` - 3DES 加密解密
- `spiderkit.downloader`
  - `Downloader` - 异步文件下载器
  - `M3U8Downloader` - M3U8 视频下载器
- `spiderkit.storage`
  - `save_to_csv` - 保存数据到 CSV 文件
  - `save_to_json` - 保存数据到 JSON 文件
  - `save_to_jsonl` - 保存数据到 JSONL 文件
- `spiderkit.utils`
  - `parse_font` / `decrypt_text_with_font_maps` / `FontParseConfig` - 字体解析与解密
  - `md5` / `sha1` / `sha224` / `sha256` / `sha384` / `sha512` / `sha3_256` - 哈希函数
  - `blake2b` / `blake2s` - BLAKE2 哈希函数
  - `to_json` / `convert_keys_to_snake_case` / `parse_cookies` - 通用工具函数
- `spiderkit.config`
  - `SpiderKitConfig` / `get_config` / `set_config` - 全局配置管理

## 快速开始

### 加密解密

```python
import os
from spiderkit.crypto import (
    generate_rsa_keypair, rsa_encrypt, rsa_encrypt_long, rsa_decrypt,
    aes_encrypt, aes_decrypt, des_encrypt, des_decrypt
)

plaintext = "Hello World!"

# RSA 加密解密
public_key, private_key = generate_rsa_keypair(key_size=2048)
rsa_encrypted = rsa_encrypt(plaintext, public_key, "OAEP", hash_algorithm="SHA256")
print(rsa_encrypted)
rsa_decrypted = rsa_decrypt(rsa_encrypted, private_key, "OAEP", hash_algorithm="SHA256")
print(rsa_decrypted)

# RSA 长文本分块加密
long_text = "这是一段很长的文本..." * 100
long_encrypted = rsa_encrypt_long(long_text, public_key, "OAEP")
print(long_encrypted)

# AES 加密解密
aes_key = os.urandom(32)
aes_iv = os.urandom(16)
aes_encrypted = aes_encrypt(plaintext, aes_key, "CBC", iv=aes_iv, output_format="base64")
print(aes_encrypted)
aes_decrypted = aes_decrypt(aes_encrypted, aes_key, "CBC", iv=aes_iv)
print(aes_decrypted)

# DES 加密解密
des_key = os.urandom(8)
des_encrypted = des_encrypt(plaintext, des_key, "ECB", output_format="hex")
print(des_encrypted)
des_decrypted = des_decrypt(des_encrypted, des_key, "ECB")
print(des_decrypted)
```

### 异步下载

```python
from spiderkit.downloader import Downloader, M3U8Downloader

# 可选请求头 (部分网站加了防盗链需要 Referer 字段)
headers = {
    "Referer": "https://www.example.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 普通文件下载
downloader = Downloader(
    headers=headers,
    concurrency=16,
    timeout=10,
    max_retries=3,
    retry_delay=1.0
)
file_mapping = {
    "images/image1.jpg": "https://example.com/image1.jpg",
    "images/image2.jpg": "https://example.com/image2.jpg",
    "images/image3.jpg": "https://example.com/image3.jpg"
}
downloader.download_files(file_mapping)

# M3U8 视频下载 (需安装 ffmpeg)
m3u8_downloader = M3U8Downloader(headers=headers, concurrency=32)
m3u8_downloader.download_video(
    "https://example.com/video.m3u8",
    "output_video.mp4",
    cleanup_temp=True
)
```

### 字体解析

```python
from spiderkit.utils import parse_font, decrypt_text_with_font_maps, FontParseConfig

# 解析字体文件 (支持本地路径或 URL)
font_maps = parse_font(
    "https://example.com/font.woff",
    download_dir="./fonts",
    save_json=True,
    json_file_path="./fonts/font_maps.json"
)

# 自定义解析配置
config = FontParseConfig(
    image_size=400,
    font_size=240,
    include_unicode_escape=True
)
font_maps = parse_font("fonts/font.ttf")

# 解密文本
encrypted_text = "加密的文本内容"
decrypted_text = decrypt_text_with_font_maps(encrypted_text, font_maps)
print(decrypted_text)
```

### 哈希计算

```python
from spiderkit.utils import (
    md5, sha1, sha224, sha256, sha384, sha512,
    sha3_256, blake2b, blake2s
)

text = "Hello World!"

# 默认输出 hex 格式
print(md5(text))
print(sha1(text))
print(sha256(text))
print(sha512(text))

# SHA-2 系列
print(sha224(text))
print(sha384(text))

# SHA-3 系列
print(sha3_256(text))

# BLAKE2 系列
print(blake2b(text))
print(blake2s(text))

# 其他输出格式: binary / base64
print(md5(text, "binary"))
print(md5(text, "base64"))
print(sha256(text, "hex"))
```

### 数据存储

```python
from spiderkit.storage import save_to_csv, save_to_json, save_to_jsonl

data = [
    {"name": "张三", "age": 25, "city": "北京"},
    {"name": "李四", "age": 30, "city": "上海"}
]

# 保存为 CSV (支持追加模式)
save_to_csv(data, "data/users.csv", mode="a", encoding="utf-8-sig")

# 保存为 JSON (自动合并已有数据)
save_to_json(data, "data/users.json", mode="a", ensure_ascii=False, indent=2)

# 保存为 JSONL (每行一个 JSON 对象)
save_to_jsonl(data, "data/users.jsonl", mode="a", ensure_ascii=False)
```

### 通用工具

```python
from spiderkit.utils import to_json, convert_keys_to_snake_case, parse_cookies

# JSON 序列化
data = {"name": "张三", "age": 25}
json_str = to_json(data, indent=2)
print(json_str)

# 键名转换为 snake_case
camel_case_data = {
    "firstName": "张三",
    "lastName": "李",
    "userInfo": {"phoneNumber": "123456"}
}
snake_case_data = convert_keys_to_snake_case(camel_case_data)
print(snake_case_data)

# Cookies 解析
cookies_str = "session=abc123; user_id=456; token=xyz789"
cookies_dict = parse_cookies(cookies_str)
print(cookies_dict)

# 也支持字典输入
cookies_dict = parse_cookies({"session": "abc123", "user_id": 456})
print(cookies_dict)
```

## 使用建议

- `Downloader.download_files` 内部使用 `asyncio.run`, 若你已处于事件循环中, 请在外部自行编排协程
- 数据存储默认输出目录为 `./data`, 写入模式默认 `a` (追加)
- M3U8 下载需要安装 `ffmpeg`, 确保命令行可用
- 字体解析使用 OCR 识别, 准确率取决于字体清晰度

## 配置

SpiderKit 提供统一配置入口, 可在运行时调整行为或用环境变量覆盖

```python
from spiderkit.config import get_config, set_config, SpiderKitConfig

# 获取全局配置
config = get_config()
print(config.downloader_concurrency)
print(config.storage_default_dir)

# 修改配置
config.downloader_concurrency = 32
config.downloader_timeout = 30
config.storage_default_dir = "./exports"
config.log_level = "DEBUG"
set_config(config)

# 创建新配置实例
new_config = SpiderKitConfig(
    downloader_concurrency=64,
    downloader_timeout=60,
    storage_default_dir="./output",
    log_level="INFO"
)
set_config(new_config)
```

常用环境变量:

- `SPIDERKIT_DOWNLOADER_CONCURRENCY` - 下载并发数 (默认 16)
- `SPIDERKIT_DOWNLOADER_TIMEOUT` - 下载超时时间 (默认 10 秒)
- `SPIDERKIT_DOWNLOADER_MAX_RETRIES` - 最大重试次数 (默认 3)
- `SPIDERKIT_DOWNLOADER_RETRY_DELAY` - 重试延迟时间 (默认 1.0 秒)
- `SPIDERKIT_FONT_SIZE` - 字体渲染大小 (默认 240)
- `SPIDERKIT_FONT_IMAGE_SIZE` - 字体图片大小 (默认 400)
- `SPIDERKIT_FONT_DOWNLOAD_TIMEOUT` - 字体下载超时 (默认 15 秒)
- `SPIDERKIT_STORAGE_DEFAULT_FORMAT` - 默认存储格式 (默认 csv)
- `SPIDERKIT_STORAGE_DEFAULT_DIR` - 默认存储目录 (默认 ./data)
- `SPIDERKIT_STORAGE_DEFAULT_MODE` - 默认写入模式 (默认 a)
- `SPIDERKIT_LOG_LEVEL` - 日志级别 (默认 INFO)
- `SPIDERKIT_TEMP_DIR` - 临时文件目录 (默认 None)
- `SPIDERKIT_CLEANUP_TEMP_FILES` - 是否清理临时文件 (默认 true)
