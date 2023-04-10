from pathlib import Path

from praatio import textgrid as tg
from praatio.data_classes.textgrid_tier import TextgridTier


def get_test_tier(file: Path) -> TextgridTier:
    grid = tg.openTextgrid(file, includeEmptyIntervals=True)
    return grid.tierDict["TestTier"]