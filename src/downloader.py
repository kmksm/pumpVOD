import asyncio
from src.models import Clip, Segment
from configuration import (
    CACHE_DIR,
    DOWNLOAD_BASE_URL,
    SEGMENTS_DIR,
    MAX_CONCURRENT_DOWNLOADS,
)
from pathlib import Path
from src.logger import logger, terminal_log, LogLevel
from curl_cffi import requests


class CacheExists:
    pass


async def download_segments(
    clip: Clip,
    segment_indexes: list[int],
    download_dir: Path = CACHE_DIR,
    use_cache: bool = True,
    concurrency: int = MAX_CONCURRENT_DOWNLOADS,
) -> list[Segment]:
    """
    Download a list of segments for a given clip.

    :param clip: The `Clip` object.
    :param segment_indexes: The indexes of the segments to download.
    :param download_dir: The directory where the segment will be saved.
    :param use_cache: If True, will not re-download segments that already exist.
    :param concurrency: Maximum number of concurrent downloads allowed.
    :return: A list of `Segment` objects representing the downloaded segments.
    """

    async def _download_segment(
        idx: int, session: requests.AsyncSession, segment: Segment
    ) -> requests.Response | CacheExists:
        nonlocal _segments_downloaded

        if segment.filepath.exists() and use_cache:
            logger.debug(
                f"[{idx} / {len(segments)}] Segment {segment.index} already exists"
            )
            _segments_downloaded += 1

            terminal_log(
                f"[{_segments_downloaded} / {len(segments)}] Downloading segments...",
                level=LogLevel.DEBUG,
                end="\r",
            )
            return CacheExists

        async with semaphore:
            logger.debug(
                f"[{idx} / {len(segments)}] Downloading segment: {segment.index}"
            )

            while True:
                try:
                    response: requests.Response = await session.get(
                        segment.download_url, impersonate="chrome110"
                    )
                    break
                except requests.exceptions.ConnectionError as e:
                    logger.exception(
                        f"Connection error occurred while downloading segment {segment.index}"
                        f": {e}. Retrying in 3 seconds..."
                    )
                    await asyncio.sleep(3)
                    continue

            response.raise_for_status()

            logger.debug(
                f"[{idx} / {len(segments)}] Response received for segment {segment.index}. "
                f"Status code: {response.status_code}. "
                f"Response length: {len(response.content)} bytes."
            )
            _segments_downloaded += 1
            terminal_log(
                f"[{_segments_downloaded} / {len(segments)}] Downloading segments...",
                level=LogLevel.DEBUG,
                end="\r",
            )

        return response

    semaphore = asyncio.Semaphore(concurrency)

    logger.debug(f"Downloading segments for {str(clip)}")

    segments: list[Segment] = []

    for segment_index in segment_indexes:
        segment_download_url = (
            f"{DOWNLOAD_BASE_URL}/{clip.coin_id}/{clip.clip_id_parts[1]}/"
            f"segment_{clip.clip_id_mystery_part}_{segment_index:05d}.ts"
        )
        segment_download_path = (
            download_dir
            / clip.download_dir
            / SEGMENTS_DIR
            / f"seg_{segment_index:05d}.ts"
        )

        segments.append(
            Segment(
                clip=clip,
                index=segment_index,
                download_url=segment_download_url,
                filepath=segment_download_path,
                timestamp=None,
            )
        )

    logger.debug(f"Constructed {len(segments)} Segments for download")

    terminal_log(f"Downloading {len(segments)} segments for clip")
    _segments_downloaded = 0

    async with requests.AsyncSession() as session:
        results = await asyncio.gather(
            *[
                _download_segment(idx=segment_idx, session=session, segment=segment)
                for segment_idx, segment in enumerate(segments, 1)
            ]
        )

    for idx, result in enumerate(results):
        if result is CacheExists:
            continue

        segment = segments[idx]
        segment.filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(segment.filepath, "wb") as file:
            file.write(result.content)

    logger.debug(f"Downloaded {len(segments)} segments for {str(clip)}")

    terminal_log(
        f"Downloaded all {len(segments)} segments for clip",
        level=LogLevel.SUCCESS,
    )

    return segments


def make_concat_file(segments: list[Segment], destination: Path) -> None:
    """
    Create a file listing all segments to be concatenated.

    :param segments: List of `Segment` objects.
    :param destination: Path where the concat file will be created.
    :return: Path to the created concat file.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)

    with open(destination, "w") as concat_file:
        for segment in segments:
            concat_file.write(f"file '{segment.filepath.absolute()}'\n")
