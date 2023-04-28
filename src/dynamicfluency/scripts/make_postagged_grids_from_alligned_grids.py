#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse

from praatio import textgrid as tg
from praatio.data_classes.textgrid import Textgrid
from praatio.data_classes.interval_tier import IntervalTier

from dynamicfluency.pos_tagging import make_pos_tier
from dynamicfluency.helpers import get_local_glob


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Creates a textgrid with a POS-tagged tier from an allignment textgrid"
    )
    parser.add_argument(
        "-d",
        "--directory",
        nargs="?",
        default="output",
        help="The directory the tokens and phases is expected in, and the output is saved to",
    )
    parser.add_argument(
        "-a",
        "--allignment",
        help="The type of allignment textgrid, either 'maus' or 'aeneas'",
    )

    args = parser.parse_args()

    if not Path(args.directory).exists():
        parser.error(f"{args.directory} does not exist")

    return args


def main():
    args: argparse.Namespace = parse_arguments()

    if args.allignment == "maus":
        tokentier_name = "ORT-MAU"
    elif args.allignment == "aeneas":
        tokentier_name = "Words"
    else:
        raise ValueError(f"Unknown allignment type found: {args.allignment}")

    allignment_files = get_local_glob(args.directory, glob="*.allignment.TextGrid")

    for file in allignment_files:
        allignment_grid = tg.openTextgrid(str(file), includeEmptyIntervals=True)

        if not isinstance(
            tier := allignment_grid.tierDict[tokentier_name], IntervalTier
        ):
            raise ValueError("Cannot read Allignment: Not an interval tier")

        tagged_tier = make_pos_tier(tier)

        tag_grid = Textgrid()
        tag_grid.addTier(tagged_tier)

        name = str(file).replace(".allignment.TextGrid", ".pos_tags.TextGrid")
        tag_grid.save(name, format="long_textgrid", includeBlankSpaces=True)


if __name__ == "__main__":
    main()
