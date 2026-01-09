"""异步下载器实现

提供高性能异步文件下载
"""

import asyncio
from pathlib import Path

import aiohttp
import aiofiles
from tqdm import tqdm
from loguru import logger

from ..config import get_config


class Downloader:
    """异步文件下载器"""

    def __init__(
            self,
            headers: dict[str, str] | None = None,
            concurrency: int | None = None,
            timeout: int | None = None,
            max_retries: int | None = None,
            retry_delay: float | None = None,
    ):
        """初始化下载器

        Args:
            headers: HTTP 请求头
            concurrency: 并发数量
            timeout: 请求超时时间
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间
        """
        config = get_config()
        self.headers = headers or config.downloader_headers
        self.semaphore = asyncio.Semaphore(concurrency or config.downloader_concurrency)
        self.timeout = aiohttp.ClientTimeout(total=timeout or config.downloader_timeout)
        self.max_retries = max_retries or config.downloader_max_retries
        self.retry_delay = retry_delay or config.downloader_retry_delay

    async def _fetch_url_content(self, session: aiohttp.ClientSession, url: str) -> bytes | None:
        """获取 URL 内容

        Args:
            session: HTTP 会话
            url: 目标 URL

        Returns:
            文件内容字节数据, 失败时返回 None
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                async with session.get(url, headers=self.headers, timeout=self.timeout) as response:
                    response.raise_for_status()
                    return await response.read()
            except Exception:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"获取 URL 内容失败: {url}")
                    return None
        return None

    @staticmethod
    async def _write_to_file(file_path: str, content: bytes) -> bool:
        """将内容写入文件

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            写入成功返回 True, 失败返回 False
        """
        if not content:
            return False
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(file_path, "wb") as file:
                await file.write(content)
            return True
        except Exception:
            logger.exception(f"文件写入失败: {file_path}")
            return False

    async def _download_single_file(self, session: aiohttp.ClientSession, file_path: str, url: str) -> bool:
        """下载单个文件

        Args:
            session: HTTP 会话
            file_path: 保存路径
            url: 下载 URL

        Returns:
            下载成功返回 True, 失败返回 False
        """
        async with self.semaphore:
            content = await self._fetch_url_content(session, url)
            return await self._write_to_file(file_path, content)

    async def _download_multiple_files(self, file_url_mapping: dict[str, str]) -> None:
        """批量下载文件

        Args:
            file_url_mapping: 文件路径到 URL 的映射
        """
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit=0), timeout=self.timeout) as session:
                tasks = [self._download_single_file(session, file_path, url) for file_path, url in file_url_mapping.items()]
                successful_downloads = 0
                with tqdm(total=len(tasks), desc="下载文件中") as pbar:
                    for future in asyncio.as_completed(tasks):
                        result = await future
                        if result:
                            successful_downloads += 1
                        pbar.update(1)
                        pbar.set_postfix(success=successful_downloads, total=len(tasks))
                logger.info(f"下载完成: {successful_downloads}/{len(tasks)} 个文件成功")
        except Exception:
            logger.exception("批量下载文件失败")
            raise

    def download_files(self, file_url_mapping: dict[str, str]) -> None:
        """下载文件

        Args:
            file_url_mapping: 文件路径到 URL 的映射字典
        """
        try:
            if not file_url_mapping:
                logger.warning("没有文件需要下载")
                return
            asyncio.run(self._download_multiple_files(file_url_mapping))
        except Exception:
            logger.exception("文件下载失败")
            raise
