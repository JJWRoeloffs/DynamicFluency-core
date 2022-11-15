import os
import csv
from typing import List
from itertools import chain

from praatio import textgrid as tg
from praatio.data_classes.textgrid_tier import TextgridTier

from dynamicfluency.repetitions import make_freqdist_tier, make_repetitions_tier
from dynamicfluency.pos_tagging import make_pos_tier
from dynamicfluency.helpers import pos_tier_to_lemma_tier, split_pos_label


def get_test_tier(file: str) -> TextgridTier:
    grid = tg.openTextgrid(file, includeEmptyIntervals=True)
    return grid.tierDict["TestTier"]


def get_valid_tags(file: str) -> List:
    with open(file, "r") as f:
        tags = csv.reader(f)
        return list(*tags)


class TestRepetitionsTier:
    original_tier = get_test_tier(
        os.path.join("tests", "data", "testgrid_pos.TextGrid")
    )
    tier = make_repetitions_tier(
        pos_tier=get_test_tier(os.path.join("tests", "data", "testgrid_pos.TextGrid")),
        to_ignore=("uhm"),
        # TODO test cache size by adding one more to the end that should be ignored
        # TODO test empty lines to be ignored
    )

    def test_tier_length(self):
        assert len(self.tier.entryList) == len(self.original_tier.entryList)

    def test_timestamps(self):
        assert self.tier.minTimestamp == self.original_tier.minTimestamp == 0
        assert self.tier.maxTimestamp == self.original_tier.maxTimestamp == 7.1

    def test_entry_timestamps(self):
        for new, original in zip(self.tier.entryList, self.original_tier.entryList):
            assert new.start == original.start
            assert new.end == original.end

    def test_first_occurrence(self):
        # text = "a_DT"
        assert self.tier.entryList[0].label == "0"
        # text = "aal_NV"
        assert self.tier.entryList[2].label == "0"

    def test_immediate_occurrence(self):
        # text = "a_DT" // immediatly after
        assert self.tier.entryList[1].label == "1.0"

    def test_later_occurrence(self):
        # text = "a_DT" // 1 in between
        assert self.tier.entryList[3].label == "0.5"

    def test_ignored_ignored(self):
        # text = "uhm" // in to_ignore
        assert self.tier.entryList[4].label == "uhm"

    def test_ignored_skipped_over(self):
        # text = "aal_NV" // 2 in between, but 1 of those in to_ignore.
        assert self.tier.entryList[5].label == "0.5"


class TestFreqdistTier:
    original_tier = get_test_tier(
        os.path.join("tests", "data", "testgrid_pos.TextGrid")
    )
    tier = make_freqdist_tier(
        pos_tier=get_test_tier(os.path.join("tests", "data", "testgrid_pos.TextGrid")),
        to_ignore=("uhm"),
    )

    def test_tier_length(self):
        assert len(self.tier.entryList) == len(self.original_tier.entryList)

    def test_timestamps(self):
        assert self.tier.minTimestamp == self.original_tier.minTimestamp == 0
        assert self.tier.maxTimestamp == self.original_tier.maxTimestamp == 7.1

    def test_entry_timestamps(self):
        for new, original in zip(self.tier.entryList, self.original_tier.entryList):
            assert new.start == original.start
            assert new.end == original.end

    def test_regular_tier(self):
        # text = "a_DT"
        assert self.tier.entryList[0].label == "0.5"
        # text = "a_DT"
        assert self.tier.entryList[1].label == "0.5"
        # text = "aal_NV"
        assert self.tier.entryList[2].label == str(1 / 3)
        #   text = "a_DT"
        assert self.tier.entryList[3].label == "0.5"
        # text = "aal_NV"
        assert self.tier.entryList[5].label == str(1 / 3)

    def test_ignored_ignored(self):
        # text = "uhm" // in to_ignore
        assert self.tier.entryList[4].label == "uhm"


class TestPosTier:
    original_tier = get_test_tier(
        os.path.join("tests", "data", "testgrid_lemma.TextGrid")
    )
    tier = make_pos_tier(
        get_test_tier(os.path.join("tests", "data", "testgrid_lemma.TextGrid")),
    )

    def test_tier_length(self):
        assert len(self.tier.entryList) == len(self.original_tier.entryList)

    def test_timestamps(self):
        assert self.tier.minTimestamp == self.original_tier.minTimestamp == 0
        assert self.tier.maxTimestamp == self.original_tier.maxTimestamp == 7.1

    def test_entry_timestamps(self):
        for new, original in zip(self.tier.entryList, self.original_tier.entryList):
            assert new.start == original.start
            assert new.end == original.end

    def test_lemma_preservation_as_lowercase(self):
        lemmas = pos_tier_to_lemma_tier(self.tier)
        for new, original in zip(lemmas.entryList, self.original_tier.entryList):
            assert new.label == original.label.lower()

    def test_entry_pos_tags(self):
        possible_tags = get_valid_tags(
            os.path.join("tests", "data", "valid_pos_tags.csv")
        )
        for entry in self.tier.entryList:
            tags = split_pos_label(entry.label, get_pos=True).split(" ")
            for tag in tags:
                assert tag in possible_tags
