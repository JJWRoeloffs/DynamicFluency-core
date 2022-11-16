import os
import sqlite3
import pandas
import csv

from typing import List, Dict
from praatio import textgrid as tg

from dynamicfluency.word_frequencies import *
from dynamicfluency.helpers import connect_to_database


def create_mock_database_from_file(file: str) -> sqlite3.Cursor:
    database: sqlite3.Connection = sqlite3.connect(":memory:")
    df = pandas.DataFrame = pandas.read_csv(
        file, sep=",", index_col="Lemma", dtype=str, engine="python"
    )
    df.to_sql("Mock", database)
    database.row_factory = sqlite3.Row
    return database.cursor()


def read_mock_databse_as_csv(file: str) -> List[Dict]:
    with open(file) as f:
        data = list(csv.DictReader(f))
    return data


class TestSQL:
    cursor = create_mock_database_from_file(
        os.path.join("tests", "data", "testlemma.csv")
    )

    def test_mock_cursor(self):
        assert isinstance(self.cursor, sqlite3.Cursor)
        assert self.cursor.row_factory is sqlite3.Row
        lemma = self.cursor.execute("SELECT Lemma from Mock ORDER BY Lemma").fetchone()
        assert lemma["Lemma"] == "a"

    def test_connect_to_database(self):
        cursor = connect_to_database(":memory:")
        assert isinstance(cursor, sqlite3.Cursor)
        assert cursor.row_factory is sqlite3.Row


class TestFrequencyGrid:
    data = read_mock_databse_as_csv(os.path.join("tests", "data", "testlemma.csv"))
    correct_lemma = [
        "Lemma",
        "FREQcount",
        "CDcount",
        "FREQlow",
        "Cdlow",
        "SUBTLWF",
        "Lg10WF",
        "SUBTLCD",
        "Lg10CD",
        "Dom_PoS_SUBTLEX",
        "Freq_dom_PoS_SUBTLEX",
        "Percentage_dom_PoS",
        "All_PoS_SUBTLEX",
        "All_freqs_SUBTLEX",
    ]
    original_tier = tg.openTextgrid(
        os.path.join("tests", "data", "testgrid_lemma.TextGrid"),
        includeEmptyIntervals=True,
    ).tierDict["TestTier"]
    grid = create_frequency_grid(
        lemma_tier=(
            tg.openTextgrid(
                os.path.join("tests", "data", "testgrid_lemma.TextGrid"),
                includeEmptyIntervals=True,
            ).tierDict["TestTier"]
        ),
        cursor=create_mock_database_from_file(
            os.path.join("tests", "data", "testlemma.csv")
        ),
        table_name="Mock",
        to_ignore=("uhm", "aardvark"),
    )

    def test_grid_timestamps(self):
        assert self.grid.minTimestamp == self.original_tier.minTimestamp == 0
        assert self.grid.maxTimestamp == self.original_tier.maxTimestamp == 7.1

    def test_tier_names(self):
        tiers = self.grid.tierDict.keys()
        assert len(self.correct_lemma) == len(tiers)
        for name, lemma in zip(tiers, self.correct_lemma):
            assert isinstance(name, str)
            assert name == lemma

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
                == 7.1
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

    def test_tiers_missing_data(self):
        for tier_name in self.grid.tierDict.keys():
            entryList = self.grid.tierDict[tier_name].entryList
            # text = "isn't" // not in the csv
            assert entryList[6].label == "MISSING"
