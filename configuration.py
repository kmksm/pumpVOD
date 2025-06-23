import sys
from dotenv import dotenv_values
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
elif __file__:
    BASE_DIR = Path(__file__).parent

TRUE_VALUES = {"1", "true", "t", "y", "yes"}
CONSOLE_LOG_LEVEL = "INFO"

config_values = dotenv_values("config.cfg")

PROMPT_SECONDS = config_values.get("PROMPT_SECONDS", "true").lower() in TRUE_VALUES
SECONDS_AFTER = int(config_values.get("SECONDS")) or 30
SECONDS_BEFORE = int(config_values.get("SECONDS_BEFORE")) or 10

CACHE_DIR = BASE_DIR / "cache"
DOWNLOAD_DIR = BASE_DIR / "clips"
EXECUTION_LOGS_DIR = BASE_DIR / ".execution_logs"

SECONDS_PER_SEGMENT = 2
SEGMENTS_DIR = "_segments"
DOWNLOAD_BASE_URL = "https://clips.pump.fun"

# Maximum number of concurrent downloads allowed for segments.
MAX_CONCURRENT_DOWNLOADS = int(config_values.get("MAX_CONCURRENT_DOWNLOADS", 5))

# Output video codec for the final video encoding
# Using "libx264" for H.264 encoding, which is widely supported and provides
# a good balance between quality and file size.
OUTPUT_CODEC = "libx264"

# Output CRF (Constant Rate Factor) for video encoding
# Lower values mean better quality, but larger file sizes.
# Typical values range from `18` (high quality) to `28` (lower quality).
# `24` is a good default for a balance between quality and file size.
OUTPUT_CRF = 24
