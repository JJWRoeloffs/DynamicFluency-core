#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from praatio import textgrid as tg
from praatio.data_classes.interval_tier import IntervalTier

from dynamicfluency.helpers import get_local_glob
from dynamicfluency.syntactic_analysis import make_syntax_grid


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Creates textgrid with syntactic information already present in pos tags"
    )
    parser.add_argument(
        "-d",
        "--directory",
        nargs="?",
        default="output",
        help="The directory the tokens and phases is expected in, and the output is saved to",
    )

    args = parser.parse_args()

    if not Path(args.directory).exists():
        parser.error(f"{args.directory} does not exist")

    return args


def main():
    args: argparse.Namespace = parse_arguments()

    tagged_files = get_local_glob(args.directory, glob="*.pos_tags.TextGrid")

    for file in tagged_files:
        tagged_grid = tg.openTextgrid(str(file), includeEmptyIntervals=True)

        if not isinstance(tier := tagged_grid.tierDict["POStags"], IntervalTier):
            raise ValueError("Cannot read POStags: Not an interval tier")

        syntax_grid = make_syntax_grid(pos_tier=tier)

        name = str(file).replace(".pos_tags.TextGrid", ".syntax.TextGrid")
        syntax_grid.save(name, format="long_textgrid", includeBlankSpaces=True)


if __name__ == "__main__":
    main()
