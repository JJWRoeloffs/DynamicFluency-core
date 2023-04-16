from __future__ import annotations

from pathlib import Path

from dynamicfluency.data import DATAFILE, get_valid_tags


class TestDataFile:
    def test_data_files(self):
        assert isinstance(DATAFILE, Path)
        assert DATAFILE.exists()
        assert DATAFILE.is_file()
        assert DATAFILE.suffix == ".csv"
        assert DATAFILE.is_absolute()
        assert not DATAFILE.is_reserved()

    def test_data_tags(self):
        tags = get_valid_tags()
        assert isinstance(tags, list)
        assert tags
        for tag in tags:
            assert isinstance(tag, str)
