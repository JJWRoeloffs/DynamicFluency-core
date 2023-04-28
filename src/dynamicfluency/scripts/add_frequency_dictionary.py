#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import csv
import sqlite3
from pathlib import Path

import pandas


# Allow for reading very big files
MAXSIZE = sys.maxsize
while True:
    try:
        csv.field_size_limit(MAXSIZE)
        break
    except Exception:
        MAXSIZE //= 2


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Creates a SQLite3 database from a csv-like file"
    )
    requiredNamed = parser.add_argument_group("Required named arguments")

    requiredNamed.add_argument(
        "-t",
        "--table_name",
        help="Name of the table to be created This has to be unique for this dictionary.",
        required=True,
    )
    requiredNamed.add_argument(
        "-f",
        "--dictionary_file",
        help='csv-like file file location to read from. WordForms have to be in a column named "WordForm"',
        required=True,
    )

    parser.add_argument(
        "-b",
        "--database_file",
        nargs="?",
        default="databases/main.db",
        help="File used for the SQLite Database.",
    )
    parser.add_argument(
        "-s",
        "--seperator",
        nargs="?",
        default=",",
        help='Seperator used in the database file. Tabs would be "\\t", commas ",", for example',
    )
    parser.add_argument(
        "-e",
        "--if_exists",
        choices=["fail", "replace"],
        nargs="?",
        default="fail",
        help='What to do if a table with the specified name already exists in the database. Either "fail" or "replace"',
    )
    args = parser.parse_args()

    if args.table_name == "default":
        parser.error(
            "Table name cannot be 'default'. This would cause naming conflicts"
        )

    if not Path(args.database_file).exists():
        parser.error(f"{args.database_file} does not exist")

    if not Path(args.dictionary_file).exists():
        parser.error(f"{args.dictionary_file} does not exist")

    return args


def read_file(file: str, *, sep: str = " ") -> pandas.DataFrame:
    """Read file into Pandas dataframe with correct constraints.
    Trowing an understadable error when user puts in bad data"""
    try:
        return pandas.read_csv(
            file, sep=sep, index_col="WordForm", dtype=str, engine="python"
        )
    except ValueError as error:
        print(
            """Unable to read file (Make the word_forms in the specified file are in a column named \"WordForm\")

Error text generated by Python: \n""",
            error,
        )
        sys.exit()


def main():
    args: argparse.Namespace = parse_arguments()
    df: pandas.DataFrame = read_file(args.dictionary_file, sep=args.seperator)

    with sqlite3.connect(args.database_file) as database:
        try:
            df.to_sql(args.table_name, database, if_exists=args.if_exists)
        except ValueError as error:
            print("Cannot write to SQL Database\n", error)


if __name__ == "__main__":
    main()
