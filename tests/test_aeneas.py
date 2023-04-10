import pytest
from pathlib import Path

from praatio.utilities.errors import TextgridStateError
from praatio.data_classes.interval_tier import IntervalTier

from dynamicfluency.aeneas_conversion import aeneas_tier_from_file


class TestAeneasTierFromFile:
    bad_file = Path(__file__).parent.joinpath("data", "test_aeneas_bad.json")
    good_file = Path(__file__).parent.joinpath("data", "test_aeneas_good.json")

    def test_bad_file_raises_without_force(self):
        with pytest.raises(TextgridStateError):
            interval_tier = aeneas_tier_from_file(
                self.bad_file, "BadTier", force_validity=False
            )

    def test_bad_file_completes_when_forced(self):
        interval_tier = aeneas_tier_from_file(
            self.bad_file, "BadTier", force_validity=True
        )
        assert isinstance(interval_tier, IntervalTier)
        assert interval_tier.name == "BadTier"

    @pytest.mark.parametrize("force", [True, False])
    def test_good_file_completes(self, force):
        interval_tier = aeneas_tier_from_file(
            self.good_file, "GoodTier", force_validity=force
        )
        assert isinstance(interval_tier, IntervalTier)
        assert interval_tier.name == "GoodTier"

    @pytest.mark.parametrize("force", [True, False])
    def test_good_file_gets_correct_values(self, force):
        interval_tier = aeneas_tier_from_file(
            self.good_file, "GoodTier", force_validity=force
        )
        # {
        #     "begin": "0.000",
        #     "children": [],
        #     "end": "3.400",
        #     "id": "f000001",
        #     "language": "eng",
        #     "lines": [
        #         "This"
        #     ]
        # },
        assert interval_tier.entryList[0].start == 0
        assert interval_tier.entryList[0].end == 3.4
        assert interval_tier.entryList[0].label == "This"
        # {
        #     "begin": "3.400",
        #     "children": [],
        #     "end": "5.200",
        #     "id": "f000002",
        #     "language": "eng",
        #     "lines": [
        #         "is"
        #     ]
        # },
        assert interval_tier.entryList[1].start == 3.4
        assert interval_tier.entryList[1].end == 5.2
        assert interval_tier.entryList[1].label == "is"
        # {
        #     "begin": "5.200",
        #     "children": [],
        #     "end": "5.400",
        #     "id": "f000003",
        #     "language": "eng",
        #     "lines": [
        #         "a"
        #     ]
        # },
        assert interval_tier.entryList[2].start == 5.2
        assert interval_tier.entryList[2].end == 5.4
        assert interval_tier.entryList[2].label == "a"
        # {
        #     "begin": "5.400",
        #     "children": [],
        #     "end": "5.880",
        #     "id": "f000004",
        #     "language": "eng",
        #     "lines": [
        #         "good"
        #     ]
        # },
        assert interval_tier.entryList[3].start == 5.4
        assert interval_tier.entryList[3].end == 5.88
        assert interval_tier.entryList[3].label == "good"
        # {
        #     "begin": "5.880",
        #     "children": [],
        #     "end": "6.200",
        #     "id": "f000005",
        #     "language": "eng",
        #     "lines": [
        #         "aeneas"
        #     ]
        # },
        assert interval_tier.entryList[4].start == 5.88
        assert interval_tier.entryList[4].end == 6.20
        assert interval_tier.entryList[4].label == "aeneas"
        # {
        #     "begin": "6.200",
        #     "children": [],
        #     "end": "6.560",
        #     "id": "f000006",
        #     "language": "eng",
        #     "lines": [
        #         "test"
        #     ]
        # },
        assert interval_tier.entryList[5].start == 6.2
        assert interval_tier.entryList[5].end == 6.56
        assert interval_tier.entryList[5].label == "test"
        # {
        #     "begin": "6.560",
        #     "children": [],
        #     "end": "7.080",
        #     "id": "f000007",
        #     "language": "eng",
        #     "lines": [
        #         "file"
        #     ]
        # }
        assert interval_tier.entryList[6].start == 6.56
        assert interval_tier.entryList[6].end == 7.08
        assert interval_tier.entryList[6].label == "file"

    def test_bad_file_gets_correct_labels(self):
        interval_tier = aeneas_tier_from_file(
            self.bad_file, "GoodTier", force_validity=True
        )
        assert interval_tier.entryList[0].label == "This"
        assert interval_tier.entryList[1].label == "is"
        assert interval_tier.entryList[2].label == "a"
        assert interval_tier.entryList[3].label == "bad"
        assert interval_tier.entryList[4].label == "aeneas"
        assert interval_tier.entryList[5].label == "test"
        assert interval_tier.entryList[6].label == "file"
