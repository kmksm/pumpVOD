from dataclasses import dataclass
from configuration import SECONDS_PER_SEGMENT
from urllib.parse import unquote, parse_qs, urlparse
from pathlib import Path
import re


@dataclass
class Clip:
    coin_id: str
    clip_id: str

    def __str__(self) -> str:
        return f"<Clip:{self.coin_id}-{self.clip_id}>"

    @staticmethod
    def from_url(url: str) -> "Clip":
        unquoted_url = unquote(url)
        parsed_url = urlparse(unquoted_url)
        query_params = parse_qs(parsed_url.query)

        split_path = parsed_url.path.split("/")

        if len(split_path) < 3 or split_path[1] != "coin" or "clip" not in query_params:
            raise Exception("Unexpected URL format!")

        return Clip(coin_id=split_path[2], clip_id=query_params["clip"][0])

    @property
    def download_dir(self) -> str:
        """Directory name where the clip segments should be saved."""
        return self.clip_id.replace(":", "-")

    @property
    def clip_id_parts(self) -> tuple[str, str]:
        """Split the clip ID into its components."""
        return tuple(self.clip_id.split(":", 1))

    @property
    def clip_id_mystery_part(self) -> str:
        """Return ~MySterY part of the clip ID."""
        return self.clip_id_parts[1].split("_", 1)[1]


@dataclass
class Timestamp:
    hours: int
    minutes: int
    seconds: int

    def __str__(self) -> str:
        return f"<Timestamp-{self.hours:02}:{self.minutes:02}:{self.seconds:02}>"

    def __add__(self, seconds: int) -> "Timestamp":
        return Timestamp.from_seconds(self.total_seconds + seconds)

    def __sub__(self, seconds: int) -> "Timestamp":
        return Timestamp.from_seconds(max(0, self.total_seconds - seconds))

    @property
    def total_seconds(self) -> int:
        return self.hours * 3600 + self.minutes * 60 + self.seconds

    @property
    def human(self) -> str:
        return f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}"

    @property
    def machine(self) -> str:
        return f"{self.hours:02}-{self.minutes:02}-{self.seconds:02}"

    @staticmethod
    def from_seconds(seconds: int) -> "Timestamp":
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return Timestamp(hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def from_string(timestamp_str: str) -> "Timestamp":
        pattern = re.compile(r"((?P<h>\d+):)?(?P<m>[0-5]?[0-9]):(?P<s>[0-5]?[0-9])")
        match_result = re.match(pattern, timestamp_str)

        if match_result is None:
            raise Exception("Pattern match failed")

        return Timestamp(*(int(v or 0) for v in match_result.groupdict().values()))

    def to_segment_index(self, seconds_per_segment: int = SECONDS_PER_SEGMENT) -> int:
        return (
            self.hours * 3600 + self.minutes * 60 + self.seconds
        ) // seconds_per_segment


@dataclass
class Segment:
    clip: Clip
    index: int
    download_url: str
    filepath: Path
    timestamp: Timestamp | None = None
