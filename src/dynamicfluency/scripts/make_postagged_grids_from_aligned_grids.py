#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse

from praatio import textgrid as tg
from praatio.data_classes.textgrid import Textgrid
from praatio.data_classes.interval_tier import IntervalTier
from dynamicfluency.model_data import VALID_LANGUAGES

from dynamicfluency.pos_tagging import make_pos_tier
from dynamicfluency.helpers import get_local_glob


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Creates a textgrid with a POS-tagged tier from an alignment textgrid"
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
        "--alignment",
        help="The type of alignment textgrid, 'maus' or 'aeneas' or 'whisper'",
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

    if args.alignment == "maus":
        tokentier_name = "ORT-MAU"
    elif args.alignment == "aeneas":
        tokentier_name = "Words"
    elif args.alignment == "whisper":
        tokentier_name = "words_text"
    else:
        raise ValueError(f"Unknown alignment type found: {args.alignment}")

    alignment_files = get_local_glob(args.directory, glob="*.alignment.TextGrid")

    for file in alignment_files:
        alignment_grid = tg.openTextgrid(str(file), includeEmptyIntervals=True)

        if not isinstance(
            tier := alignment_grid.tierDict[tokentier_name], IntervalTier
        ):
            raise ValueError("Cannot read alignment: Not an interval tier")

        tagged_tier = make_pos_tier(tier, lang=args.language)

        tag_grid = Textgrid()
        tag_grid.addTier(tagged_tier)

        name = str(file).replace(".alignment.TextGrid", ".pos_tags.TextGrid")
        tag_grid.save(name, format="long_textgrid", includeBlankSpaces=True)


if __name__ == "__main__":
    main()
