"""数据保存模块

支持 CSV, JSON, JSONL 格式的数据保存
"""

import csv
import json
from pathlib import Path

from loguru import logger


def save_to_csv(data: dict | list, filepath: str, mode: str = "a", encoding: str = "utf-8-sig", header: bool | None = None) -> None:
    """将数据保存到CSV文件

    Args:
        data: 要保存的数据, 可以是单个字典或字典列表
        filepath: 保存文件的路径, 包含文件名
        mode: 文件打开模式, 默认追加模式
        encoding: 文件编码, 默认utf-8-sig以支持Excel打开
        header: 是否保存表头, 默认None(新文件保存表头, 追加模式不保存)
    """
    try:
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        data_list = [data] if isinstance(data, dict) else data
        item_count = len(data_list)
        write_header = header
        if write_header is None:
            file_exists = file_path.exists() and file_path.stat().st_size > 0
            write_header = not (file_exists and mode == "a")
        with file_path.open(mode, newline="", encoding=encoding) as f:
            if data_list:
                writer = csv.DictWriter(f, fieldnames=list(data_list[0].keys()))
                if write_header:
                    writer.writeheader()
                writer.writerows(data_list)
        logger.success(f"成功保存 {item_count} 条数据到 CSV 文件, 文件路径: {filepath}")
    except Exception:
        logger.exception(f"保存数据到CSV文件失败, 文件路径: {filepath}")
        raise


def save_to_json(data: dict | list, filepath: str, mode: str = "a", ensure_ascii: bool = False, indent: int = 2) -> None:
    """将数据保存到JSON文件

    Args:
        data: 要保存的数据, 可以是单个字典或字典列表
        filepath: 保存文件的路径, 包含文件名
        mode: 文件打开模式, 默认追加模式
        ensure_ascii: 是否确保ASCII编码, 默认False保留Unicode字符
        indent: JSON缩进空格数, 默认2
    """
    try:
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        data_list = [data] if isinstance(data, dict) else data
        item_count = len(data_list)
        target_data = data_list
        if mode == "a" and file_path.exists() and file_path.stat().st_size > 0:
            with file_path.open("r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, list):
                target_data = existing + data_list
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(target_data, f, ensure_ascii=ensure_ascii, indent=indent)
        logger.success(f"成功保存 {item_count} 条数据到 JSON 文件, 文件路径: {filepath}")
    except Exception:
        logger.exception(f"保存数据到JSON文件失败, 文件路径: {filepath}")
        raise


def save_to_jsonl(data: dict | list, filepath: str, mode: str = "a", ensure_ascii: bool = False, indent: int | None = None) -> None:
    """将数据保存到JSONL文件

    Args:
        data: 要保存的数据, 可以是单个字典或字典列表
        filepath: 保存文件的路径, 包含文件名
        mode: 文件打开模式, 默认追加模式
        ensure_ascii: 是否确保ASCII编码, 默认False保留Unicode字符
        indent: JSON缩进空格数, 默认None不缩进
    """
    try:
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        data_list = [data] if isinstance(data, dict) else data
        item_count = len(data_list)
        with file_path.open(mode, encoding="utf-8") as f:
            for item in data_list:
                json_str = json.dumps(item, ensure_ascii=ensure_ascii, indent=indent)
                f.write(json_str + "\n")
        logger.success(f"成功保存 {item_count} 条数据到 JSONL 文件, 文件路径: {filepath}")
    except Exception:
        logger.exception(f"保存数据到JSONL文件失败, 文件路径: {filepath}")
        raise
