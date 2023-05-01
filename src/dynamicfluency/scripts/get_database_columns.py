#!/usr/bin/env python3
from __future__ import annotations

import csv
import argparse
from pathlib import Path
import sqlite3

from dynamicfluency.helpers import get_row_cursor
from dynamicfluency.word_frequencies import get_column_names


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reads the collumns from an SQLite3 database. Presents the found names inside a .csv in the output directory to allow it to be read by praat"
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
        help="The directory the text file is saved to.",
    )

    args = parser.parse_args()

    if not Path(args.database).exists():
        parser.error(f"{args.database} does not exist")

    if not Path(args.directory).exists():
        parser.error(f"{args.directory} does not exist")

    return args


def main():
    args: argparse.Namespace = parse_arguments()

    filepath = Path().resolve().joinpath(args.directory, "column_names.csv")

    # As far as I am aware, there is no good way to send an error message like this back to praat.
    if filepath.exists():
        print(f"{str(filepath)} already exists")
        print("Cannot write anywhere.")
        return

    with sqlite3.connect(args.database) as connection:
        cursor = get_row_cursor(connection)
        names = get_column_names(cursor, table_name=args.table_name)

    if not names:
        names = ["DYNAMICFLUENCY-ERROR - Incorrect table name?"]
    elif not "WordForm" in names:
        names = ["DYNAMICFLUENCY-ERROR - No column 'WordForm' found."]

    names = [name for name in names if name != "WordForm"]

    with filepath.open("w", encoding="utf-8") as f:
        csv.writer(f).writerow(names)


if __name__ == "__main__":
    main()
