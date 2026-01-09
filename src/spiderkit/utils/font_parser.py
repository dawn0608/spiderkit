"""字体解析模块实现

提供反爬虫字体文件解析和文本解密功能
"""

import json
import hashlib
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional
from contextlib import suppress
from dataclasses import dataclass
from urllib.parse import urlparse

from loguru import logger
from ddddocr import DdddOcr
from fontTools.ttLib import TTFont
from PIL.ImageFont import FreeTypeFont
from PIL import Image, ImageDraw, ImageFont

from ..config import get_config


@dataclass(frozen=True)
class FontParseConfig:
    """字体解析配置"""

    image_size: int = 400
    font_size: int = 240
    background: tuple = (255, 255, 255, 255)
    color: tuple = (0, 0, 0, 255)
    include_unicode_escape: bool = False


def _save_font_maps(font_maps: dict[str, str], json_file_path: str | Path) -> None:
    """保存字体映射到 JSON 文件, 并合并已有内容

    Args:
        font_maps: 字体映射字典
        json_file_path: JSON 文件路径
    """
    try:
        json_path = Path(json_file_path)
        existing_data: dict[str, str] = {}
        with suppress(Exception):
            with json_path.open("r", encoding="utf-8") as file:
                existing_data = json.load(file)
        merged_maps = {**existing_data, **font_maps}
        if json_path.parent:
            json_path.parent.mkdir(parents=True, exist_ok=True)
        with json_path.open("w", encoding="utf-8") as file:
            json.dump(merged_maps, file, ensure_ascii=False, indent=4)
        existing_keys = set(existing_data.keys())
        new_keys = set(font_maps.keys())
        added = len(new_keys - existing_keys)
        updated = len(font_maps) - added
        logger.success(f"保存字体映射到 {json_path}: 新增 {added} 项, 更新 {updated} 项, 共 {len(merged_maps)} 项")
    except Exception:
        logger.exception("保存字体映射失败")
        raise


def _render_char_image(font: FreeTypeFont, char: str, config: Optional[FontParseConfig] = None) -> Optional[Image.Image]:
    """渲染指定字符为图片

    Args:
        font: 字体对象
        char: 需要渲染的字符
        config: 字体解析配置

    Returns:
        渲染后的图片, 无法渲染时返回 None
    """
    try:
        if config is None:
            global_config = get_config()
            config = FontParseConfig(
                image_size=global_config.font_image_size,
                font_size=global_config.font_size,
                background=global_config.font_background,
                color=global_config.font_color,
                include_unicode_escape=global_config.font_include_unicode_escape,
            )
        bbox = font.getbbox(char)
        if not bbox:
            return None
        image = Image.new("RGBA", (config.image_size, config.image_size), config.background)
        draw = ImageDraw.Draw(image)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (config.image_size - text_width) // 2 - bbox[0]
        y = (config.image_size - text_height) // 2 - bbox[1]
        draw.text((x, y), char, fill=config.color, font=font)
        return image.convert("RGB")
    except Exception:
        logger.exception(f"渲染字符图片失败: {char}")
        return None


def _recognize_char(font: FreeTypeFont, ocr: DdddOcr, char: str, config: Optional[FontParseConfig] = None) -> str:
    """识别指定字符的 OCR 结果

    Args:
        font: 字体对象
        ocr: OCR 识别器
        char: 需要识别的字符
        config: 字体解析配置

    Returns:
        OCR 识别结果, 识别失败时返回空字符串
    """
    try:
        image = _render_char_image(font, char, config)
        if not image:
            return ""
        return ocr.classification(image).strip()
    except Exception:
        logger.exception(f"字符识别失败: {char}")
        return ""


def _iter_font_chars(font_data: TTFont) -> list:
    """遍历字体文件中包含的字符

    Args:
        font_data: 字体数据对象

    Returns:
        字符列表
    """
    try:
        cmap = font_data.getBestCmap() or {}
        return [chr(codepoint) for codepoint in sorted(cmap)]
    except Exception:
        logger.exception("遍历字体字符失败")
        raise


def _build_download_path(font_url: str, download_dir: Optional[str | Path]) -> Path:
    """构建字体下载路径

    Args:
        font_url: 字体文件 URL
        download_dir: 下载目录, 为空时使用临时目录

    Returns:
        下载文件路径
    """
    try:
        parsed = urlparse(font_url)
        filename = Path(parsed.path).name or "font.ttf"
        if not Path(filename).suffix:
            filename = f"{filename}.ttf"
        fingerprint = hashlib.sha1(font_url.encode("utf-8")).hexdigest()[:8]
        final_name = f"{fingerprint}_{filename}"
        if download_dir is None:
            download_dir = tempfile.mkdtemp(prefix="font_download_")
        download_path = Path(download_dir)
        download_path.mkdir(parents=True, exist_ok=True)
        return download_path / final_name
    except Exception:
        logger.exception("构建字体下载路径失败")
        raise


def _download_font_file(font_source: str | Path, download_dir: Optional[str | Path] = None, timeout: Optional[int] = None) -> Path:
    """解析字体来源并返回本地路径(必要时下载)

    Args:
        font_source: 字体文件 URL 或本地路径
        download_dir: 下载目录, 为空时使用临时目录
        timeout: 下载超时时间, 为空时使用全局配置

    Returns:
        字体文件本地路径
    """
    try:
        if timeout is None:
            timeout = get_config().font_download_timeout
        if not font_source:
            raise ValueError("字体来源不能为空")

        if isinstance(font_source, Path):
            if font_source.exists():
                return font_source
            raise ValueError(f"本地字体文件不存在: {font_source}")

        parsed = urlparse(font_source)
        if parsed.scheme and parsed.scheme not in {"http", "https", "file"}:
            raise ValueError(f"不支持的字体 URL 协议: {parsed.scheme}")

        if parsed.scheme == "file":
            return Path(parsed.path)

        if not parsed.scheme:
            local_path = Path(font_source).expanduser()
            if local_path.exists():
                return local_path
            raise ValueError(f"本地字体文件不存在: {font_source}")

        download_path = _build_download_path(font_source, download_dir)
        if download_path.exists():
            return download_path

        request = urllib.request.Request(font_source, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content = response.read()

        with download_path.open("wb") as file:
            file.write(content)

        logger.info(f"已下载字体文件: {download_path}")
        return download_path
    except Exception:
        logger.exception("下载字体文件失败")
        raise


def parse_font(font_source: str | Path, download_dir: Optional[str | Path] = None, save_json: bool = False, json_file_path: Optional[str | Path] = None) -> dict:
    """解析字体文件并生成字符映射

    Args:
        font_source: 字体文件 URL 或本地路径
        download_dir: 下载目录, 仅 URL 时生效, 为空时使用临时目录
        save_json: 是否保存字体映射到 JSON 文件
        json_file_path: JSON 文件路径, 为空时使用字体文件同名路径

    Returns:
        字体映射字典
    """
    try:
        font_path = _download_font_file(font_source, download_dir=download_dir)

        config = FontParseConfig()
        if config is None:
            global_config = get_config()
            config = FontParseConfig(
                image_size=global_config.font_image_size,
                font_size=global_config.font_size,
                background=global_config.font_background,
                color=global_config.font_color,
                include_unicode_escape=global_config.font_include_unicode_escape,
            )
        ocr = DdddOcr(show_ad=False)
        font_maps: dict[str, str] = {}

        with TTFont(font_path) as font_data:
            pil_font = ImageFont.truetype(str(font_path), size=config.font_size)

            for char in _iter_font_chars(font_data):
                recognized_char = _recognize_char(pil_font, ocr, char, config)
                if not recognized_char:
                    logger.warning(f"跳过无法识别字符: {char}")
                    continue

                font_maps[char] = recognized_char
                if config.include_unicode_escape:
                    font_maps[f"\\u{ord(char):04x}"] = recognized_char
                logger.success(f"映射字体字符: {char} -> {recognized_char}")

        if save_json:
            if json_file_path is None:
                json_file_path = font_path.with_suffix(".json")
            _save_font_maps(font_maps, json_file_path)

        return font_maps
    except Exception:
        logger.exception("解析字体文件失败")
        raise


def decrypt_text_with_font_maps(encrypted_text: str, font_maps: dict[str, str]) -> str:
    """使用字体映射解密文本内容, 未匹配字符保持原样

    Args:
        encrypted_text: 加密文本
        font_maps: 字体映射字典

    Returns:
        解密后的文本
    """
    try:
        return "".join(font_maps.get(char, font_maps.get(f"\\u{ord(char):04x}", char)) for char in encrypted_text)
    except Exception:
        logger.exception("使用字体映射解密文本失败")
        raise
