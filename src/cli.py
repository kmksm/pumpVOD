from argparse import ArgumentParser


def get_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="pump.fun clip downloader",
    )
    # Main options
    parser.add_argument(
        "clip_url",
        type=str,
        nargs="?",
        default=None,
        help="URL of the clip to download.",
    )

    # # Timestamp options
    parser.add_argument(
        "--timestamp",
        "-t",
        type=str,
        default=None,
        dest="timestamp",
        help="Timestamp to start from in the `HH:MM:SS` format",
    )
    parser.add_argument(
        "--seconds",
        "-s",
        type=int,
        default=None,
        dest="seconds",
        help="Number of seconds to download starting from the timestamp.",
    )
    parser.add_argument(
        "--seconds-before",
        "-b",
        type=int,
        default=None,
        dest="seconds_before",
        help="Number of seconds to download before the timestamp.",
    )

    return parser
