#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from praatio import textgrid as tg
from praatio.data_classes.interval_tier import IntervalTier

from dynamicfluency.helpers import get_row_cursor, get_local_glob
from dynamicfluency.word_frequencies import create_frequency_grid


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Reads word frequencies from an SQLite3 database. Assumes word_forms are in a column called "WordForm"'
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

    if not Path(args.database).exists():
        parser.error(f"{args.database} does not exist")

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

        with sqlite3.connect(args.database) as connection:
            cursor = get_row_cursor(connection)
            frequency_grid = create_frequency_grid(
                word_form_tier=tier,
                cursor=cursor,
                table_name=args.table_name,
                to_ignore=args.to_ignore,
                rows=args.rows,
            )

        frequency_grid.removeTier("WordForm")

        name = str(file).replace(".allignment.TextGrid", ".frequencies.TextGrid")
        frequency_grid.save(name, format="long_textgrid", includeBlankSpaces=True)


if __name__ == "__main__":
    main()
