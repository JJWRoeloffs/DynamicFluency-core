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
        "--alignment",
        help="The type of alignment textgrid, 'maus' or 'aeneas' or 'whisper'",
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
        "-c",
        "--columns",
        nargs="?",
        default="",
        help="The Columns to read from the database table, seperated by commas",
    )

    args: argparse.Namespace = parser.parse_args()

    args.to_ignore = args.to_ignore.split(",") if args.to_ignore is not None else None

    if args.columns == "DYNAMICFLUENCY-DEFAULT":
        args.columns = None

    args.columns = args.columns.split(",") if args.columns else None

    if args.columns is not None and not "WordForm" in args.columns:
        args.columns.append("WordForm")

    if not Path(args.database).exists():
        parser.error(f"{args.database} does not exist")

    if not Path(args.directory).exists():
        parser.error(f"{args.directory} does not exist")

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

        with sqlite3.connect(args.database) as connection:
            cursor = get_row_cursor(connection)
            frequency_grid = create_frequency_grid(
                word_form_tier=tier,
                cursor=cursor,
                table_name=args.table_name,
                to_ignore=args.to_ignore,
                columns=args.columns,
            )

        frequency_grid.removeTier("WordForm")

        name = str(file).replace(".alignment.TextGrid", ".frequencies.TextGrid")
        frequency_grid.save(name, format="long_textgrid", includeBlankSpaces=True)


if __name__ == "__main__":
    main()
