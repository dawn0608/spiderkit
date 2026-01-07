"""数据保存模块

支持 CSV、JSON、JSONL 格式的数据保存
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from loguru import logger
from config import get_config


def save_data_to_file(data: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str, file_format: Optional[str] = None, output_dir: Optional[str] = None,
                      mode: Optional[str] = None) -> None:
    """保存数据到指定格式文件

    Args:
        data: 待保存的数据, 支持单条字典或列表嵌套字典
        filename: 文件名, 不包含扩展名
        file_format: 保存格式, 支持 csv, json, jsonl, 为空时使用全局配置
        output_dir: 输出目录, 为空时使用全局配置
        mode: 文件写入模式, 为空时使用全局配置

    Returns:
        无

    Raises:
        Exception: 保存过程中出现异常时抛出
    """
    try:
        if not data:
            logger.warning("没有数据需要保存")
            return

        config = get_config()
        file_format = file_format or config.storage_default_format
        output_dir = output_dir or config.storage_default_dir
        mode = mode or config.storage_default_mode

        file_path = _build_file_path(output_dir, filename, file_format)

        if file_format == "csv":
            records = _normalize_records(data)
            _save_csv(records, file_path, mode)
        elif file_format == "json":
            _save_json(data, file_path, mode)
        elif file_format == "jsonl":
            records = _normalize_records(data)
            _save_jsonl(records, file_path, mode)
        else:
            raise ValueError(f"不支持的保存格式: {file_format}")
    except Exception:
        logger.exception("保存数据失败")
        raise


def _build_file_path(output_dir: str, filename: str, file_format: str) -> Path:
    """构建输出文件路径

    Args:
        output_dir: 输出目录
        filename: 文件名
        file_format: 文件格式

    Returns:
        输出文件路径

    Raises:
        Exception: 路径构建失败时抛出
    """
    try:
        base_dir = Path(output_dir)
        file_path = base_dir / f"{filename}.{file_format}"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path
    except Exception:
        logger.exception("构建输出路径失败")
        raise


def _normalize_records(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """统一为字典列表, 仅支持单条字典或字典列表."""
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return data
    raise TypeError("数据格式必须是字典或由字典组成的列表")


def _record_count(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> int:
    """获取数据条数."""
    return 1 if isinstance(data, dict) else len(data)


def _save_csv(data: List[Dict[str, Any]], file_path: Path, mode: str) -> None:
    """保存数据为 CSV

    Args:
        data: 待保存的数据列表
        file_path: 文件路径
        mode: 文件写入模式

    Returns:
        无

    Raises:
        Exception: 保存失败时抛出
    """
    try:
        file_exists = file_path.exists() and file_path.stat().st_size > 0
        with open(file_path, mode, newline="", encoding="utf-8-sig") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=list(data[0].keys()))
            if mode == "w" or not file_exists:
                writer.writeheader()
            writer.writerows(data)
        logger.success(f"成功保存 {len(data)} 条数据到 {file_path}")
    except Exception:
        logger.exception("保存CSV文件失败")
        raise


def _save_json(data: Union[Dict[str, Any], List[Dict[str, Any]]], file_path: Path, mode: str) -> None:
    """保存数据为 JSON

    Args:
        data: 待保存的数据
        file_path: 文件路径
        mode: 文件写入模式

    Returns:
        无

    Raises:
        Exception: 保存失败时抛出
    """
    try:
        if not isinstance(data, dict) and not (isinstance(data, list) and all(isinstance(item, dict) for item in data)):
            raise TypeError("JSON 数据格式必须是字典或由字典组成的列表")

        target_data = data
        if mode == "a" and file_path.exists() and file_path.stat().st_size > 0:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                existing = json.load(file_handle)
            if isinstance(existing, list):
                if isinstance(data, dict):
                    target_data = existing + [data]
                else:
                    target_data = existing + data

        with open(file_path, "w", encoding="utf-8") as file_handle:
            json.dump(target_data, file_handle, ensure_ascii=False, indent=2)
        logger.success(f"成功保存 {_record_count(data)} 条数据到 {file_path}")
    except Exception:
        logger.exception("保存JSON文件失败")
        raise


def _save_jsonl(data: List[Dict[str, Any]], file_path: Path, mode: str) -> None:
    """保存数据为 JSON Lines

    Args:
        data: 待保存的数据列表
        file_path: 文件路径
        mode: 文件写入模式

    Returns:
        无

    Raises:
        Exception: 保存失败时抛出
    """
    try:
        with open(file_path, mode, encoding="utf-8") as file_handle:
            for item in data:
                file_handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        logger.success(f"成功保存 {len(data)} 条数据到 {file_path}")
    except Exception:
        logger.exception("保存JSONL文件失败")
        raise
