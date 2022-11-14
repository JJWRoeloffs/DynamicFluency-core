#!/usr/bin/env python3
from __future__ import annotations

import glob
import argparse

from praatio import textgrid as tg
from praatio.data_classes.textgrid import Textgrid

from dynamicfluency.pos_tagging import make_pos_tier


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
    return parser.parse_args()


def main():
    args: argparse.Namespace = parse_arguments()

    if args.allignment == "maus":
        tokentier_name = "ORT-MAU"
    elif args.allignment == "aeneas":
        tokentier_name = "Words"
    else:
        raise ValueError(f"Unknown allignment type found: {args.allignment}")

    allignment_files = glob.glob(f"./{args.directory}/*.allignment.TextGrid")

    for file in allignment_files:
        allignment_grid = tg.openTextgrid(file, includeEmptyIntervals=True)

        tagged_tier = make_pos_tier(allignment_grid.tierDict[tokentier_name])

        tag_grid = Textgrid()
        tag_grid.addTier(tagged_tier)
        name = file.replace(".allignment.TextGrid", ".pos_tags.TextGrid")
        tag_grid.save(name, format="long_textgrid", includeBlankSpaces=True)


if __name__ == "__main__":
    main()
