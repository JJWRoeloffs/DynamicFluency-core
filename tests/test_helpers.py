import os
import pytest

from praatio import textgrid as tg
from praatio.data_classes.textgrid_tier import TextgridTier
from praatio.utilities.constants import Interval, Point

from dynamicfluency.helpers import *
from .test_tier_generation import get_test_tier


class TestSplitLabels:
    def test_normal_label(self):
        assert split_pos_label("is_VB") == "is"
        assert split_pos_label("to_TO") == "to"
        assert split_pos_label("split_VB") == "split"

    def test_complex_label(self):
        assert split_pos_label("is_VB n't_RB") == "isn't"
        assert split_pos_label("has_VB n't_RB") == "hasn't"

    def test_overly_complex_label(self):
        assert split_pos_label("would_VB n't_RB 've_VB") == "wouldn't've"

    def test_normal_label_pos(self):
        assert split_pos_label("is_VB", get_pos=True) == "VB"
        assert split_pos_label("to_TO", get_pos=True) == "TO"
        assert split_pos_label("split_VB", get_pos=True) == "VB"

    def test_complex_label_pos(self):
        assert split_pos_label("is_VB n't_RB", get_pos=True) == "VB RB"
        assert split_pos_label("has_VB n't_RB", get_pos=True) == "VB RB"

    def test_overly_complex_label_pos(self):
        assert split_pos_label("would_VB n't_RB 've_VB", get_pos=True) == "VB RB VB"


class TestPosTierConversion:
    original_tier = get_test_tier(
        os.path.join("tests", "data", "testgrid_pos.TextGrid")
    )
    tier = pos_tier_to_lemma_tier(
        get_test_tier(os.path.join("tests", "data", "testgrid_pos.TextGrid"))
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

    def test_entry_split(self):
        for new, original in zip(self.tier.entryList, self.original_tier.entryList):
            assert new.label == split_pos_label(original.label)


class TestReplaceLabel:
    interval = Interval(1.2, 1.5, "Test_string")
    point = Point(1.5, "Test_string")

    def test_static_interval(self):
        new_interval = replace_label(self.interval, lambda x: x)
        assert isinstance(new_interval, Interval)
        assert new_interval.start == self.interval.start
        assert new_interval.end == self.interval.end
        assert new_interval.label == self.interval.label

    def test_alphabet_interval(self):
        new_interval = replace_label(self.interval, lambda x: "".join(sorted(x)))
        assert isinstance(new_interval, Interval)
        assert new_interval.start == self.interval.start
        assert new_interval.end == self.interval.end
        assert new_interval.label == "T_eginrsstt"

    def test_replacement_interval(self):
        new_interval = replace_label(self.interval, lambda x: "Hello!")
        assert isinstance(new_interval, Interval)
        assert new_interval.start == self.interval.start
        assert new_interval.end == self.interval.end
        assert new_interval.label == "Hello!"

    def test_static_point(self):
        new_point = replace_label(self.point, lambda x: x)
        assert isinstance(new_point, Point)
        assert new_point.time == self.point.time
        assert new_point.label == self.point.label

    def test_alphabet_point(self):
        new_point = replace_label(self.point, lambda x: "".join(sorted(x)))
        assert isinstance(new_point, Point)
        assert new_point.time == self.point.time
        assert new_point.label == "T_eginrsstt"

    def test_replacement_point(self):
        new_point = replace_label(self.point, lambda x: "Hello!")
        assert isinstance(new_point, Point)
        assert new_point.time == self.point.time
        assert new_point.label == "Hello!"


class TestLabelsToString:
    def test_lemma(self):
        lemma_tier = get_test_tier(
            os.path.join("tests", "data", "testgrid_lemma.TextGrid")
        )
        assert (
            entrylist_labels_to_string(lemma_tier.entryList)
            == "a A aal aardvark uhm isn't"
        )

    def test_lemma_to_ignore(self):
        lemma_tier = get_test_tier(
            os.path.join("tests", "data", "testgrid_lemma.TextGrid")
        )
        assert (
            entrylist_labels_to_string(lemma_tier.entryList, to_ignore=["uhm"])
            == "a A aal aardvark isn't"
        )

    def test_converted_lemma(self):
        lemma_tier = pos_tier_to_lemma_tier(
            get_test_tier(os.path.join("tests", "data", "testgrid_pos.TextGrid"))
        )
        assert (
            entrylist_labels_to_string(lemma_tier.entryList)
            == "a a aal a uhm aal aal some some a aal"
        )

    def test_converted_lemma_to_ignore(self):
        lemma_tier = pos_tier_to_lemma_tier(
            get_test_tier(os.path.join("tests", "data", "testgrid_pos.TextGrid"))
        )
        assert (
            entrylist_labels_to_string(lemma_tier.entryList, to_ignore=["uhm"])
            == "a a aal a aal aal some some a aal"
        )

    def test_pos(self):
        pos_tier = get_test_tier(os.path.join("tests", "data", "testgrid_pos.TextGrid"))
        assert (
            entrylist_labels_to_string(pos_tier.entryList)
            == "a_DT a_DT aal_JJ a_DT uhm aal_JJ aal_JJ some_JJ some_NV a_DT aal_JJ"
        )

    def test_pos_to_ignore(self):
        pos_tier = get_test_tier(os.path.join("tests", "data", "testgrid_pos.TextGrid"))
        assert (
            entrylist_labels_to_string(pos_tier.entryList, to_ignore=["uhm"])
            == "a_DT a_DT aal_JJ a_DT aal_JJ aal_JJ some_JJ some_NV a_DT aal_JJ"
        )


class TestLowercaseEntryList:
    def test_lemma_length(self):
        lemma_tier = get_test_tier(
            os.path.join("tests", "data", "testgrid_lemma.TextGrid")
        )
        lowercase_lemma_list = make_lowercase_entrylist(lemma_tier.entryList)
        assert len(lowercase_lemma_list) == len(lemma_tier.entryList)

    def test_lemma_entries(self):
        lemma_tier = get_test_tier(
            os.path.join("tests", "data", "testgrid_lemma.TextGrid")
        )
        lowercase_lemma_list = make_lowercase_entrylist(lemma_tier.entryList)

        for lowercase, normal in zip(lowercase_lemma_list, lemma_tier.entryList):
            assert normal.label.lower() == lowercase.label

    def test_pos_length(self):
        pos_tier = get_test_tier(os.path.join("tests", "data", "testgrid_pos.TextGrid"))
        lowercase_pos_list = make_lowercase_entrylist(pos_tier.entryList)
        assert len(lowercase_pos_list) == len(pos_tier.entryList)

    def test_lemma_entries(self):
        pos_tier = get_test_tier(os.path.join("tests", "data", "testgrid_pos.TextGrid"))
        lowercase_pos_list = make_lowercase_entrylist(pos_tier.entryList)

        for lowercase, normal in zip(lowercase_pos_list, pos_tier.entryList):
            assert normal.label.lower() == lowercase.label


class TestSetAllTiersStatic:
    test_grid = tg.openTextgrid(
        os.path.join("tests", "data", "testgrid_manytiers.TextGrid"),
        includeEmptyIntervals=True,
    )
    original_grid = tg.openTextgrid(
        os.path.join("tests", "data", "testgrid_manytiers.TextGrid"),
        includeEmptyIntervals=True,
    )

    def test_grid_timestamps(self):
        set_all_tiers_static(self.test_grid, item="TestString", index=1)
        assert self.test_grid.minTimestamp == self.original_grid.minTimestamp
        assert self.test_grid.maxTimestamp == self.original_grid.maxTimestamp

    def test_tier_names(self):
        set_all_tiers_static(self.test_grid, item="TestString", index=1)
        test_tiers = self.test_grid.tierDict.keys()
        original_tiers = self.original_grid.tierDict.keys()
        assert len(test_tiers) == len(original_tiers)
        for test, original in zip(test_tiers, original_tiers):
            assert test == original

    def test_grid_length(self):
        set_all_tiers_static(self.test_grid, item="TestString", index=1)
        test_tiers = self.test_grid.tierDict.keys()
        original_tiers = self.original_grid.tierDict.keys()
        for test, original in zip(test_tiers, original_tiers):
            assert len(self.test_grid.tierDict[test].entryList) == len(
                self.original_grid.tierDict[original].entryList
            )

    def test_tiers_timestamp(self):
        set_all_tiers_static(self.test_grid, item="TestString", index=1)
        test_tiers = self.test_grid.tierDict.keys()
        original_tiers = self.original_grid.tierDict.keys()
        for test, original in zip(test_tiers, original_tiers):
            assert (
                self.test_grid.tierDict[test].minTimestamp
                == self.original_grid.tierDict[original].minTimestamp
            )
            assert (
                self.original_grid.tierDict[test].maxTimestamp
                == self.original_grid.tierDict[original].maxTimestamp
            )

    def test_entry_timestamps(self):
        set_all_tiers_static(self.test_grid, item="TestString", index=1)
        test_tiers = self.test_grid.tierDict.keys()
        original_tiers = self.original_grid.tierDict.keys()
        for test, original in zip(test_tiers, original_tiers):
            for test_entry, original_entry in zip(
                self.test_grid.tierDict[test].entryList,
                self.original_grid.tierDict[original].entryList,
            ):
                assert test_entry.start == original_entry.start
                assert test_entry.end == original_entry.end

    def test_set_all_tiers_st(self):
        set_all_tiers_static(self.test_grid, item="TestString", index=1)
        for tier_name in self.test_grid.tierDict.keys():
            entryList = self.test_grid.tierDict[tier_name].entryList
            assert entryList[0].label == "One"
            assert entryList[1].label == "TestString"
            assert entryList[2].label == "Three"


class TestSetAllTiersFromDict:
    test_grid = tg.openTextgrid(
        os.path.join("tests", "data", "testgrid_manytiers.TextGrid"),
        includeEmptyIntervals=True,
    )
    original_grid = tg.openTextgrid(
        os.path.join("tests", "data", "testgrid_manytiers.TextGrid"),
        includeEmptyIntervals=True,
    )
    test_dict = {
        "First": "FirstTestString",
        "Second": "SecondTestString",
        "Third": "ThirdTestString",
    }

    def test_grid_timestamps(self):
        set_all_tiers_from_dict(self.test_grid, items=self.test_dict, index=1)
        assert self.test_grid.minTimestamp == self.original_grid.minTimestamp
        assert self.test_grid.maxTimestamp == self.original_grid.maxTimestamp

    def test_tier_names(self):
        set_all_tiers_from_dict(self.test_grid, items=self.test_dict, index=1)
        test_tiers = self.test_grid.tierDict.keys()
        original_tiers = self.original_grid.tierDict.keys()
        assert len(test_tiers) == len(original_tiers)
        for test, original in zip(test_tiers, original_tiers):
            assert test == original

    def test_grid_length(self):
        set_all_tiers_from_dict(self.test_grid, items=self.test_dict, index=1)
        test_tiers = self.test_grid.tierDict.keys()
        original_tiers = self.original_grid.tierDict.keys()
        for test, original in zip(test_tiers, original_tiers):
            assert len(self.test_grid.tierDict[test].entryList) == len(
                self.original_grid.tierDict[original].entryList
            )

    def test_tiers_timestamp(self):
        set_all_tiers_from_dict(self.test_grid, items=self.test_dict, index=1)
        test_tiers = self.test_grid.tierDict.keys()
        original_tiers = self.original_grid.tierDict.keys()
        for test, original in zip(test_tiers, original_tiers):
            assert (
                self.test_grid.tierDict[test].minTimestamp
                == self.original_grid.tierDict[original].minTimestamp
            )
            assert (
                self.original_grid.tierDict[test].maxTimestamp
                == self.original_grid.tierDict[original].maxTimestamp
            )

    def test_entry_timestamps(self):
        set_all_tiers_from_dict(self.test_grid, items=self.test_dict, index=1)
        test_tiers = self.test_grid.tierDict.keys()
        original_tiers = self.original_grid.tierDict.keys()
        for test, original in zip(test_tiers, original_tiers):
            for test_entry, original_entry in zip(
                self.test_grid.tierDict[test].entryList,
                self.original_grid.tierDict[original].entryList,
            ):
                assert test_entry.start == original_entry.start
                assert test_entry.end == original_entry.end

    def test_set_all_tiers_st(self):
        set_all_tiers_from_dict(self.test_grid, items=self.test_dict, index=1)
        for tier_name in self.test_grid.tierDict.keys():
            entryList = self.test_grid.tierDict[tier_name].entryList
            assert entryList[0].label == "One"
            assert entryList[1].label == self.test_dict[tier_name]
            assert entryList[2].label == "Three"
