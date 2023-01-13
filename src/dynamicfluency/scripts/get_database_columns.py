#!/usr/bin/env python3
from __future__ import annotations

import os
import csv
import glob
import argparse

from praatio import textgrid as tg

from dynamicfluency.helpers import connect_to_database
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
    return parser.parse_args()


def main():
    args: argparse.Namespace = parse_arguments()

    filepath = f"./{args.directory}/column_names.csv"

    # As far as I am aware, there is no good way to send an error message like this back to praat.
    if os.path.exists(filepath):
        print(f"{filepath} already exists")
        print("Cannot write anywhere.")
        return

    try:
        cursor = connect_to_database(args.database)
        names = get_column_names(cursor, table_name=args.table_name)
    finally:
        cursor.connection.close()

    if not names:
        names = ["#FAIL - Incorrect table name?"]
    if not "Lemma" in names:
        names = ['#FAIL - No column "Lemma" found.']

    with open(filepath, "w") as f:
        csv.writer(f).writerow(names)


if __name__ == "__main__":
    main()
