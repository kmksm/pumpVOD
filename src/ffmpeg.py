from pathlib import Path
from sys import stdout
from subprocess import run, CompletedProcess, DEVNULL
from configuration import OUTPUT_CODEC, OUTPUT_CRF


def check_ffmpeg() -> None:
    """Check if ffmpeg is available."""
    return (
        run(
            ["ffmpeg", "-version"], stdout=DEVNULL, stderr=DEVNULL, check=True
        ).returncode
        == 0
    )


def concat(concat_file: Path, destination: Path) -> CompletedProcess:
    """
    Concatenate video segments using ffmpeg.

    :param concat_file: Path to the file listing segments to concatenate.
    :param destination: Path where the final video will be saved.
    """
    ffmpeg_command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        "-c:v",
        OUTPUT_CODEC,
        "-crf",
        str(OUTPUT_CRF),
        "-v",
        "error",
        "-stats",
        "-y",
        str(destination),
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)

    result = run(ffmpeg_command, stdout=stdout, stderr=stdout, check=True)

    if result.returncode != 0:
        raise ValueError(f"FFmpeg command failed with return code {result.returncode}")

    return result
