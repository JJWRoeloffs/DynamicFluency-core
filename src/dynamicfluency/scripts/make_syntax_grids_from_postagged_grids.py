#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from praatio import textgrid as tg
from praatio.data_classes.interval_tier import IntervalTier

from dynamicfluency.helpers import get_local_glob
from dynamicfluency.syntactic_analysis import make_syntax_grid
from dynamicfluency.model_data import VALID_LANGUAGES


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
    parser.add_argument(
        "-l",
        "--language",
        help="The language to get the tagging model of",
        choices=[x for k, v in VALID_LANGUAGES.items() for x in (k, v)],
        nargs="?",
        default="en",
    )

    args = parser.parse_args()

    if not Path(args.directory).exists():
        parser.error(f"{args.directory} does not exist")

    if args.language in VALID_LANGUAGES.values():
        [args.language] = [k for k, v in VALID_LANGUAGES.items() if v == args.language]

    if args.language not in VALID_LANGUAGES.keys():
        parser.error(f"{args.language} is not a valid language")

    return args


def main():
    args: argparse.Namespace = parse_arguments()

    tagged_files = get_local_glob(args.directory, glob="*.pos_tags.TextGrid")

    for file in tagged_files:
        tagged_grid = tg.openTextgrid(str(file), includeEmptyIntervals=True)

        if not isinstance(tier := tagged_grid.tierDict["POStags"], IntervalTier):
            raise ValueError("Cannot read POStags: Not an interval tier")

        syntax_grid = make_syntax_grid(pos_tier=tier, lang=args.language)

        name = str(file).replace(".pos_tags.TextGrid", ".syntax.TextGrid")
        syntax_grid.save(name, format="long_textgrid", includeBlankSpaces=True)


if __name__ == "__main__":
    main()
