"""M3U8 下载器实现"""

import shutil
import tempfile
import subprocess
from pathlib import Path
from urllib.parse import urljoin

import m3u8
from loguru import logger

from ..config import get_config
from .async_http_downloader import Downloader


class M3U8Downloader(Downloader):
    """M3U8 视频下载器"""

    def __init__(
            self,
            headers: dict[str, str] | None = None,
            concurrency: int | None = None,
            timeout: int | None = None,
            max_retries: int | None = None,
            retry_delay: float | None = None,
    ):
        """初始化 M3U8 下载器

        Args:
            headers: HTTP 请求头
            concurrency: 并发数量
            timeout: 请求超时时间
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间
        """
        super().__init__(headers, concurrency, timeout, max_retries, retry_delay)

    def _extract_segment_urls(self, m3u8_url: str, max_depth: int = 5, current_depth: int = 0) -> list[str]:
        """提取 M3U8 分片 URL

        Args:
            m3u8_url: M3U8 播放列表 URL
            max_depth: 最大递归深度
            current_depth: 当前递归深度

        Returns:
            分片 URL 列表
        """
        try:
            if current_depth >= max_depth:
                raise RecursionError(f"达到最大嵌套深度: {max_depth}")
            logger.info(f"处理 M3U8 [深度 {current_depth}]: {m3u8_url}")
            playlist = m3u8.load(m3u8_url)
            playlist.base_uri = m3u8_url.rsplit("/", 1)[0] + "/"
            if playlist.is_variant:
                logger.info(f"发现主播放列表, 包含 {len(playlist.playlists)} 个流")
                selected_stream = max(playlist.playlists, key=lambda p: p.stream_info.bandwidth)
                stream_url = urljoin(playlist.base_uri, selected_stream.uri)
                return self._extract_segment_urls(stream_url, max_depth, current_depth + 1)
            else:
                logger.info(f"发现媒体播放列表, 包含 {len(playlist.segments)} 个分片")
                segment_urls = []
                for segment in playlist.segments:
                    if not segment.absolute_uri:
                        segment.base_uri = playlist.base_uri
                    segment_urls.append(segment.absolute_uri)
                return segment_urls
        except Exception:
            logger.exception("提取 M3U8 分片 URL 失败")
            raise

    @staticmethod
    def _merge_and_convert_segments(segment_files: list[str], intermediate_ts_path: str, final_output_path: str) -> bool:
        """合并和转换视频分片

        Args:
            segment_files: 分片文件路径列表
            intermediate_ts_path: 中间 TS 文件路径
            final_output_path: 最终输出文件路径

        Returns:
            转换成功返回 True, 失败返回 False
        """
        file_list_path = intermediate_ts_path + ".txt"
        try:
            with open(file_list_path, "w", encoding="utf-8") as file_list:
                for file_path in segment_files:
                    file_list.write(f"file '{Path(file_path).absolute()}'\n")
            logger.info(f"合并 {len(segment_files)} 个分片")
            merge_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", file_list_path, "-c", "copy", intermediate_ts_path]
            subprocess.run(merge_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.info(f"转换为 MP4: {final_output_path}")
            convert_cmd = ["ffmpeg", "-y", "-i", intermediate_ts_path, "-c", "copy", "-movflags", "faststart", final_output_path]
            subprocess.run(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.info(f"视频转换成功: {final_output_path}")
            return True
        except Exception:
            logger.exception("合并转换过程中发生错误")
            return False
        finally:
            file_list_path_obj = Path(file_list_path)
            if file_list_path_obj.exists():
                file_list_path_obj.unlink()

    def download_video(self, m3u8_url: str, output_path: str, temp_directory: str | None = None, cleanup_temp: bool | None = None) -> None:
        """下载 M3U8 视频

        Args:
            m3u8_url: M3U8 播放列表 URL
            output_path: 输出视频文件路径
            temp_directory: 临时目录路径
            cleanup_temp: 是否清理临时文件
        """
        try:
            config = get_config()
            if cleanup_temp is None:
                cleanup_temp = config.cleanup_temp_files
            if not temp_directory:
                temp_directory = config.temp_dir or tempfile.mkdtemp(prefix="m3u8_download_")
            else:
                Path(temp_directory).mkdir(parents=True, exist_ok=True)
            segments_dir = Path(temp_directory) / "ts_segments"
            segments_dir.mkdir(parents=True, exist_ok=True)
            output_path_obj = Path(output_path)
            if output_path_obj.parent:
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            logger.info("从 M3U8 提取分片 URL")
            segment_urls = self._extract_segment_urls(m3u8_url)
            download_map = {str(segments_dir / f"segment_{idx:04d}.ts"): url for idx, url in enumerate(segment_urls)}
            logger.info(f"开始下载 {len(segment_urls)} 个分片")
            self.download_files(download_map)
            segment_files = list(download_map.keys())
            merged_ts_path = str(Path(temp_directory) / "merged_video.ts")
            logger.info("合并和转换分片")
            success = self._merge_and_convert_segments(segment_files, merged_ts_path, output_path)
            if not success:
                raise RuntimeError("视频合并转换失败")
            logger.info(f"视频成功保存到 {output_path}")
        except Exception:
            logger.exception("M3U8 视频下载失败")
            raise
        finally:
            temp_dir_path = Path(temp_directory)
            if cleanup_temp and temp_dir_path.exists():
                logger.info("清理临时文件")
                shutil.rmtree(temp_directory)
