import asyncio
from colorama import Fore, Style
from os import system, remove as remove_file
from configuration import (
    CACHE_DIR,
    DOWNLOAD_DIR,
    SECONDS_BEFORE,
    SECONDS_AFTER,
    PROMPT_SECONDS,
)
from src.models import Timestamp, Clip
from src.downloader import download_segments, make_concat_file
from src.ffmpeg import check_ffmpeg, concat as ffmpeg_concat
from src.cli import get_argument_parser
from src.logger import logger, terminal_log, LogLevel, LogObject, generate_execution_log


async def main():
    parser = get_argument_parser()
    args = vars(parser.parse_args())

    # Clip URL
    clip_url_string = args.get("clip_url")

    while True:
        if clip_url_string is None:
            terminal_log(LogObject.PREFIX)
            clip_url_string = input(
                f"{Fore.WHITE}{Style.BRIGHT}Enter the Clip URL: {Style.RESET_ALL}"
            ).strip()

        try:
            clip = Clip.from_url(clip_url_string)
            break
        except Exception as e:
            if str(e) != "Unexpected URL format!":
                raise e

            terminal_log("Invalid URL!", level=LogLevel.ERROR)
            clip_url_string = None

    # Timestamp
    timestamp_string = args.get("timestamp")

    while True:
        if timestamp_string is None:
            terminal_log(LogObject.PREFIX)
            timestamp_string = input(
                f"{Fore.WHITE}{Style.BRIGHT}Enter the Timestamp "
                f"({Fore.GREEN}HH:MM:SS{Fore.WHITE}): {Style.RESET_ALL}"
            ).strip()

        try:
            timestamp = Timestamp.from_string(timestamp_string)
            break
        except Exception as e:
            if str(e) != "Pattern match failed":
                raise e

            terminal_log("Invalid Timestamp!", LogLevel.ERROR)
            timestamp_string = None

    seconds = SECONDS_AFTER
    seconds_before = SECONDS_BEFORE

    if args.get("seconds") is not None:
        seconds = args["seconds"]
    elif PROMPT_SECONDS:
        terminal_log(LogObject.PREFIX)
        seconds = input(
            f"{Fore.WHITE}{Style.BRIGHT}Enter the number of seconds to download "
            f"(Press Enter for default {Fore.GREEN}{SECONDS_AFTER} seconds{Fore.WHITE}): "
            f"{Style.RESET_ALL}"
        ).strip()

        if seconds == "":
            seconds = SECONDS_AFTER
        else:
            seconds = int(seconds)
    else:
        seconds = SECONDS_AFTER

    if args.get("seconds_before") is not None:
        seconds_before = args["seconds_before"]
    elif PROMPT_SECONDS:
        terminal_log(LogObject.PREFIX)
        seconds_before = input(
            f"{Fore.WHITE}{Style.BRIGHT}Enter the number of seconds to download "
            "before the timestamp "
            f"(Press Enter for default {Fore.GREEN}{SECONDS_BEFORE} seconds{Fore.WHITE}): "
            f"{Style.RESET_ALL}"
        ).strip()

        if seconds_before == "":
            seconds_before = SECONDS_BEFORE
        else:
            seconds_before = int(seconds_before)
    else:
        seconds_before = SECONDS_BEFORE

    from_timestamp = timestamp - seconds_before
    to_timestamp = timestamp + seconds

    segments = await download_segments(
        clip=clip,
        segment_indexes=list(
            range(
                from_timestamp.to_segment_index(), to_timestamp.to_segment_index() + 1
            )
        ),
    )

    concat_file = CACHE_DIR / clip.download_dir / "_files_to_concat.txt"
    video_destination = (
        DOWNLOAD_DIR
        / clip.download_dir
        / f"{timestamp.machine}_{seconds_before}-{seconds}.mp4"
    )

    make_concat_file(segments, concat_file)
    concat_result = ffmpeg_concat(concat_file, video_destination)
    remove_file(concat_file)

    if concat_result.returncode != 0:
        terminal_log(
            f"Video concatenation failed with code {concat_result.returncode}.",
            level=LogLevel.ERROR,
        )
        return

    terminal_log(
        f"Video saved to: {Style.BRIGHT}{video_destination}{Style.RESET_ALL}",
        level=LogLevel.SUCCESS,
    )


if __name__ == "__main__":
    if not check_ffmpeg():
        terminal_log(
            "[FFMPEG-NOT-FOUND] FFmpeg is not available. Please, install it and try again.",
            level=LogLevel.ERROR,
        )
        system("pause")
        exit(1)

    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")

        execution_log = generate_execution_log()

        terminal_log(
            "An unexpected error occurred. Please, contact the developer\n"
            f"Execution log saved to: {execution_log}",
            level=LogLevel.ERROR,
        )
        print(
            "Unexpected error occurred. "
            "Please, contact the developer with the log file."
        )

    system("pause")
