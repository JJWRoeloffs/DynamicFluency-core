import csv
from pathlib import Path
from typing import List

from dynamicfluency.repetitions import make_freqdist_tier, make_repetitions_tier
from dynamicfluency.pos_tagging import make_pos_tier
from dynamicfluency.helpers import pos_tier_to_word_form_tier, split_pos_label

from .helpers import get_test_tier

def get_valid_tags(file: Path) -> List:
    with file.open("r") as f:
        tags = csv.reader(f)
        return list(*tags)


class TestRepetitionsTier:
    original_tier = get_test_tier(
        Path(__file__).parent.joinpath("data", "testgrid_pos.TextGrid")
    )
    tier = make_repetitions_tier(
        pos_tier=get_test_tier(Path(__file__).parent.joinpath("data", "testgrid_pos.TextGrid")),
        max_cache=5,
        to_ignore=["uhm"],
    )

    def test_tier_length(self):
        assert len(self.tier.entryList) == len(self.original_tier.entryList)

    def test_timestamps(self):
        assert self.tier.minTimestamp == self.original_tier.minTimestamp == 0
        assert self.tier.maxTimestamp == self.original_tier.maxTimestamp == 9.1

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
        # text = "aal_JJ" // 2 in between, but 1 of those in to_ignore.
        assert self.tier.entryList[5].label == "0.5"

    def test_empty_ignored(self):
        # text = ""
        assert self.tier.entryList[6].label == ""

    def test_empty_skipped_over(self):
        # text = "aal_JJ" // one empty in between.
        assert self.tier.entryList[7].label == "1.0"

    def test_max_cache_respected(self):
        # text = "aal_JJ" // 3 in between, meaning that the cashe should hold both.
        assert self.tier.entryList[11].label == "0.25"
        # text = "a_DT" // 4 in between, meaning that the cashe doesn't hold both.
        assert self.tier.entryList[10].label == "0"


class TestFreqdistTier:
    original_tier = get_test_tier(
        Path(__file__).parent.joinpath("data", "testgrid_pos.TextGrid")
    )
    tier = make_freqdist_tier(
        pos_tier=get_test_tier(Path(__file__).parent.joinpath("data", "testgrid_pos.TextGrid")),
        to_ignore=["uhm"],
    )

    def test_tier_length(self):
        assert len(self.tier.entryList) == len(self.original_tier.entryList)

    def test_timestamps(self):
        assert self.tier.minTimestamp == self.original_tier.minTimestamp == 0
        assert self.tier.maxTimestamp == self.original_tier.maxTimestamp == 9.1

    def test_entry_timestamps(self):
        for new, original in zip(self.tier.entryList, self.original_tier.entryList):
            assert new.start == original.start
            assert new.end == original.end

    def test_regular_tier(self):
        # text = "a_DT"

        assert self.tier.entryList[0].label == "0.4"
        # text = "a_DT"
        assert self.tier.entryList[1].label == "0.4"
        # text = "aal_NV"
        assert self.tier.entryList[2].label == "0.4"
        #   text = "a_DT"
        assert self.tier.entryList[3].label == "0.4"
        # text = "aal_NV"
        assert self.tier.entryList[5].label == "0.4"
        # text = "some_JJ"
        assert self.tier.entryList[8].label == "0.1"
        # text = "some_NV"
        assert self.tier.entryList[8].label == "0.1"

    def test_ignored_ignored(self):
        # text = "uhm" // in to_ignore
        assert self.tier.entryList[4].label == "uhm"

    def test_empty_ignored(self):
        # text = ""
        assert self.tier.entryList[6].label == ""


class TestPosTier:
    original_tier = get_test_tier(
        Path(__file__).parent.joinpath("data", "testgrid_word_form.TextGrid")
    )
    tier = make_pos_tier(
        get_test_tier(Path(__file__).parent.joinpath("data", "testgrid_word_form.TextGrid")),
    )

    def test_tier_length(self):
        assert len(self.tier.entryList) == len(self.original_tier.entryList)

    def test_timestamps(self):
        assert self.tier.minTimestamp == self.original_tier.minTimestamp == 0
        assert self.tier.maxTimestamp == self.original_tier.maxTimestamp == 7.2

    def test_entry_timestamps(self):
        for new, original in zip(self.tier.entryList, self.original_tier.entryList):
            assert new.start == original.start
            assert new.end == original.end

    def test_word_form_preservation_as_lowercase(self):
        word_forms = pos_tier_to_word_form_tier(self.tier)
        for new, original in zip(word_forms.entryList, self.original_tier.entryList):
            assert new.label == original.label.lower()

    def test_entry_pos_tags(self):
        possible_tags = get_valid_tags(
            Path(__file__).parent.joinpath("data", "valid_pos_tags.csv")
        )
        for entry in self.tier.entryList:
            tags = split_pos_label(entry.label, get_pos=True).split(" ")
            for tag in tags:
                assert tag in possible_tags or entry.label == ""
