#!/usr/bin/env python3
from __future__ import annotations

import glob
import argparse

from praatio import textgrid as tg

from dynamicfluency.helpers import pos_tier_to_lemma_tier, connect_to_database
from dynamicfluency.word_frequencies import create_frequency_grid


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Reads word frequencies from an SQLite3 database. Assumes lemmas are in a column called "Lemma"'
    )
    requiredNamed = parser.add_argument_group("Required named arguments")

    requiredNamed.add_argument(
        "-t", "--table_name", help="Name of the table to be read from.", required=True
    )

    parser.add_argument(
        "-b",
        "--database",
        nargs="?",
        default="databases/main.db",
        help="File used for the SQLite Database.",
    )
    parser.add_argument(
        "-d",
        "--directory",
        nargs="?",
        default="output",
        help="The directory the pos_tags .TextGrid is expected in, and the output is saved to",
    )
    parser.add_argument(
        "-i",
        "--to_ignore",
        nargs="?",
        help="The words to ignore and not assign any value, seperated by commas.",
    )

    args: argparse.Namespace = parser.parse_args()
    if args.to_ignore:
        args.to_ignore = set(args.to_ignore.split(","))
    else:
        args.to_ignore = set()
    return args


def main():
    args: argparse.Namespace = parse_arguments()

    tagged_files = glob.glob(f"./{args.directory}/*.pos_tags.TextGrid")
    for file in tagged_files:
        tagged_grid = tg.openTextgrid(file, includeEmptyIntervals=True)
        lemma_tier = pos_tier_to_lemma_tier(tagged_grid.tierDict["POStags"])

        try:
            cursor = connect_to_database(args.database)
            frequency_grid = create_frequency_grid(
                lemma_tier=lemma_tier,
                cursor=cursor,
                table_name=args.table_name,
                to_ignore=args.to_ignore,
            )
        finally:
            cursor.connection.close()

        frequency_grid.removeTier("Lemma")

        name = file.replace(".pos_tags.TextGrid", ".frequencies.TextGrid")
        frequency_grid.save(name, format="long_textgrid", includeBlankSpaces=True)


if __name__ == "__main__":
    main()
