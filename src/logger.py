from sys import stdout
from io import StringIO
from loguru import logger
from enum import StrEnum
from datetime import datetime
from pathlib import Path
from configuration import CONSOLE_LOG_LEVEL, EXECUTION_LOGS_DIR
from time import perf_counter
from colorama import Fore, Style


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


_start_time = perf_counter()
_last_log_time = _start_time


class LogObject(StrEnum):
    PREFIX = "prefix"


def terminal_log(
    text: str | LogObject, level: LogLevel = LogLevel.INFO, end: str = "\n"
) -> None:
    """
    Log a message to the terminal with the specified log level.

    :param text: The message to log.
    :param level: The log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
    """
    log_time = perf_counter()
    time_from_last_log = log_time - _last_log_time
    time_from_start = log_time - _start_time

    log_part_time = (
        f"{Fore.MAGENTA}[{Style.BRIGHT}"
        f"{time_from_start:.2f}{Style.RESET_ALL}"
        f"{Fore.MAGENTA}+{time_from_last_log:.2f}s]{Style.RESET_ALL}"
    )
    level_color = {
        LogLevel.DEBUG: Fore.BLUE,
        LogLevel.INFO: Fore.WHITE,
        LogLevel.WARNING: Fore.YELLOW,
        LogLevel.ERROR: Fore.RED,
        LogLevel.SUCCESS: Fore.GREEN,
    }.get(level, LogLevel.INFO)

    level_title = {
        LogLevel.DEBUG: "DBG",
        LogLevel.INFO: "INF",
        LogLevel.WARNING: "WRN",
        LogLevel.ERROR: "ERR",
        LogLevel.SUCCESS: "SUC",
    }.get(level, LogLevel.INFO)

    log_end = end

    if text == LogObject.PREFIX:
        level_color = Fore.CYAN
        level_title = "~~~"
        log_end = ""
        text = ""

    log_str = (
        f"{log_part_time} - {level_color}[{level_title}] - {text}{Style.RESET_ALL}"
    )

    print(log_str, end=log_end, flush=True)


def generate_execution_log() -> Path:
    """
    Generate a string representation of the execution log.

    :return: The execution log as a string.
    """
    EXECUTION_LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_file_path = (
        EXECUTION_LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    )

    with open(log_file_path, "w") as execution_log_file:
        execution_log_file.write(execution_log_buffer.getvalue())

    return log_file_path


fmt = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    " - <level>{message}</level>"
)

logger.remove()
execution_log_buffer = StringIO()

logger.add(execution_log_buffer, level="DEBUG", colorize=False, format=fmt)
logger.add(stdout, level=CONSOLE_LOG_LEVEL, colorize=True, format=fmt)
