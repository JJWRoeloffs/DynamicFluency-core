import csv
import sqlite3

from pathlib import Path
from typing import List, Dict

import pandas
from praatio import textgrid as tg
from praatio.utilities.constants import INTERVAL_TIER

from dynamicfluency.word_frequencies import *
from dynamicfluency.helpers import get_row_cursor


def create_mock_database_from_file(file: Path) -> sqlite3.Cursor:
    database: sqlite3.Connection = sqlite3.connect(":memory:")
    df = pandas.DataFrame = pandas.read_csv(
        file, sep=",", index_col="WordForm", dtype=str, engine="python"
    )
    df.to_sql("Mock", database)
    database.row_factory = sqlite3.Row
    return database.cursor()


def read_mock_databse_as_csv(file: Path) -> List[Dict]:
    with file.open("r") as f:
        return list(csv.DictReader(f))


class TestSQL:
    cursor = create_mock_database_from_file(
        Path(__file__).parent.joinpath("data", "test_word_form.csv")
    )

    def test_mock_cursor(self):
        assert isinstance(self.cursor, sqlite3.Cursor)
        assert self.cursor.row_factory is sqlite3.Row
        word_form = self.cursor.execute(
            "SELECT WordForm from Mock ORDER BY WordForm"
        ).fetchone()
        assert word_form["WordForm"] == "a"

    def test_row_cursor(self):
        with sqlite3.connect(":memory:") as connection:
            cursor = get_row_cursor(connection)
            assert isinstance(cursor, sqlite3.Cursor)
            assert cursor.row_factory is sqlite3.Row


class TestFrequencyGrid:
    data = read_mock_databse_as_csv(
        Path(__file__).parent.joinpath("data", "test_word_form.csv")
    )
    correct_word_form = [
        "WordForm",
        "FREQcount",
        "CDcount",
        "FREQlow",
        "Cdlow",
        "SUBTLWF",
        "Lg10WF",
        "SUBTLCD",
        "Lg10CD",
    ]
    original_tier = tg.openTextgrid(
        Path(__file__).parent.joinpath("data", "testgrid_word_form.TextGrid"),
        includeEmptyIntervals=True,
    ).tierDict["TestTier"]
    grid = create_frequency_grid(
        tg.openTextgrid(
            Path(__file__).parent.joinpath("data", "testgrid_word_form.TextGrid"),
            includeEmptyIntervals=True,
        ).tierDict["TestTier"],
        cursor=create_mock_database_from_file(
            Path(__file__).parent.joinpath("data", "test_word_form.csv")
        ),
        table_name="Mock",
        to_ignore=["uhm", "aardvark"],
    )

    def test_tiers_type(self):
        for tier_name in self.grid.tierDict.keys():
            assert self.grid.tierDict[tier_name].tierType == INTERVAL_TIER

    def test_grid_timestamps(self):
        assert self.grid.minTimestamp == self.original_tier.minTimestamp == 0
        assert self.grid.maxTimestamp == self.original_tier.maxTimestamp == 7.2

    def test_tier_names(self):
        tiers = self.grid.tierDict.keys()
        assert len(self.correct_word_form) == len(tiers)
        for name, word_form in zip(tiers, self.correct_word_form):
            assert isinstance(name, str)
            assert name == word_form

    def test_grid_length(self):
        for tier_name in self.grid.tierDict.keys():
            assert len(self.original_tier.entryList) == len(
                self.grid.tierDict[tier_name].entryList
            )

    def test_tiers_timestamp(self):
        for tier_name in self.grid.tierDict.keys():
            assert (
                self.grid.tierDict[tier_name].minTimestamp
                == self.original_tier.minTimestamp
                == 0
            )
            assert (
                self.grid.tierDict[tier_name].maxTimestamp
                == self.original_tier.maxTimestamp
                == 7.2
            )

    def test_entry_timestamps(self):
        for tier_name in self.grid.tierDict.keys():
            for new, original in zip(
                self.grid.tierDict[tier_name].entryList, self.original_tier.entryList
            ):
                assert new.start == original.start
                assert new.end == original.end

    def test_tiers_normal_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            #     text = "a" // in csv
            assert entryList[0].label == self.data[0][tier_name]
            #     text = "A" // in csv, but in lowercase
            assert entryList[1].label == self.data[0][tier_name]
            #     text = "  aal  " // in csv, but without trailing spaces
            assert entryList[2].label == self.data[1][tier_name]

    def test_tiers_empty_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            #     text = ""
            assert entryList[3].label == ""

    def test_tiers_ignored_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            #     text = "aardvark" // in to_ignore, in the csv
            assert entryList[4].label == ""

    def test_tiers_ignored_missing_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            # text = "uhm"  // in to_ignore and not in the csv
            assert entryList[5].label == ""

    def test_tiers_split_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            # text = "isn't" // in CSV as "isn" and "t"
            assert entryList[6].label == " ".join(
                [self.data[3][tier_name], self.data[4][tier_name]]
            )

    def test_tiers_missing_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            # text = "BLEEH" // not in the csv
            assert entryList[7].label == "MISSING"


class TestPartialFrequencyGrid:
    data = read_mock_databse_as_csv(
        Path(__file__).parent.joinpath("data", "test_word_form.csv")
    )
    correct_word_form = ["FREQcount", "CDcount", "Lg10WF", "Lg10CD"]
    original_tier = tg.openTextgrid(
        Path(__file__).parent.joinpath("data", "testgrid_word_form.TextGrid"),
        includeEmptyIntervals=True,
    ).tierDict["TestTier"]
    grid = create_frequency_grid(
        word_form_tier=(
            tg.openTextgrid(
                Path(__file__).parent.joinpath("data", "testgrid_word_form.TextGrid"),
                includeEmptyIntervals=True,
            ).tierDict["TestTier"]
        ),
        cursor=create_mock_database_from_file(
            Path(__file__).parent.joinpath("data", "test_word_form.csv")
        ),
        table_name="Mock",
        to_ignore=["uhm", "aardvark"],
        columns=correct_word_form,
    )

    def test_grid_timestamps(self):
        assert self.grid.minTimestamp == self.original_tier.minTimestamp == 0
        assert self.grid.maxTimestamp == self.original_tier.maxTimestamp == 7.2

    def test_tier_names(self):
        tiers = self.grid.tierDict.keys()
        assert len(self.correct_word_form) == len(tiers)
        for name, word_form in zip(tiers, self.correct_word_form):
            assert isinstance(name, str)
            assert name == word_form

    def test_grid_length(self):
        for tier_name in self.grid.tierDict.keys():
            assert len(self.original_tier.entryList) == len(
                self.grid.tierDict[tier_name].entryList
            )

    def test_tiers_timestamp(self):
        for tier_name in self.grid.tierDict.keys():
            assert (
                self.grid.tierDict[tier_name].minTimestamp
                == self.original_tier.minTimestamp
                == 0
            )
            assert (
                self.grid.tierDict[tier_name].maxTimestamp
                == self.original_tier.maxTimestamp
                == 7.2
            )

    def test_entry_timestamps(self):
        for tier_name in self.grid.tierDict.keys():
            for new, original in zip(
                self.grid.tierDict[tier_name].entryList, self.original_tier.entryList
            ):
                assert new.start == original.start
                assert new.end == original.end

    def test_tiers_normal_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            #     text = "a" // in csv
            assert entryList[0].label == self.data[0][tier_name]
            #     text = "A" // in csv, but in lowercase
            assert entryList[1].label == self.data[0][tier_name]
            #     text = "  aal  " // in csv, but without trailing spaces
            assert entryList[2].label == self.data[1][tier_name]

    def test_tiers_empty_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            #     text = ""
            assert entryList[3].label == ""

    def test_tiers_ignored_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            #     text = "aardvark" // in to_ignore, in the csv
            assert entryList[4].label == ""

    def test_tiers_ignored_missing_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            # text = "uhm"  // in to_ignore and not in the csv
            assert entryList[5].label == ""

    def test_tiers_split_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            # text = "isn't" // in CSV as "isn" and "t"
            assert entryList[6].label == " ".join(
                [self.data[3][tier_name], self.data[4][tier_name]]
            )

    def test_tiers_missing_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            # text = "BLEEH" // not in the csv
            assert entryList[7].label == "MISSING"
