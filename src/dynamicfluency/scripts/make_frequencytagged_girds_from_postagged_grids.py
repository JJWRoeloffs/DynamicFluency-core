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
    requiredNamed.add_argument(
        "-a",
        "--allignment",
        help="The type of allignment textgrid, either 'maus' or 'aeneas'",
        required=True,
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
        help="The directory the tokens and phases is expected in, and the output is saved to",
    )
    parser.add_argument(
        "-i",
        "--to_ignore",
        nargs="?",
        help="The words to ignore and not assign any value, seperated by commas.",
    )
    parser.add_argument(
        "-r",
        "--rows",
        nargs="?",
        default="",
        help="The Rows to read from the database table, seperated by commas",
    )

    args: argparse.Namespace = parser.parse_args()
    args.to_ignore = args.to_ignore.split(",") if args.to_ignore is not None else None
    args.rows = args.rows.split(",") if args.rows else None
    return args


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

        try:
            cursor = connect_to_database(args.database)
            frequency_grid = create_frequency_grid(
                lemma_tier=allignment_grid.tierDict[tokentier_name],
                cursor=cursor,
                table_name=args.table_name,
                to_ignore=args.to_ignore,
                rows=args.rows,
            )
        finally:
            cursor.connection.close()

        frequency_grid.removeTier("Lemma")

        name = file.replace(".allignment.TextGrid", ".frequencies.TextGrid")
        frequency_grid.save(name, format="long_textgrid", includeBlankSpaces=True)


if __name__ == "__main__":
    main()
