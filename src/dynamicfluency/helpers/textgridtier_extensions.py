from __future__ import annotations

from typing import Callable, List, Dict
from collections import namedtuple

from praatio.data_classes.textgrid import Textgrid


def replace_label(entry: namedtuple, f: Callable) -> namedtuple:
    """Returns a new namedtuple with the "label" attribute changed according to passed function."""
    as_dict = entry._asdict()
    new_label = f(as_dict.pop("label"))
    return entry.__class__(label=new_label, **as_dict)


def entrylist_labels_to_string(entryList: List[namedtuple]) -> str:
    """Make a single space-seperated string, out of the labels of an entryList
    Useful to make a "sentence" out of the words in the tier."""
    return " ".join([entry.label for entry in entryList])


def set_all_tiers_static(grid: Textgrid, *, item: str, index: int) -> None:
    """Sets the given index of all tiers' label of given grid to given value"""
    for tier in grid.tierDict:
        grid.tierDict[tier].entryList[index] = replace_label(
            grid.tierDict[tier].entryList[index], lambda x: item
        )


def set_all_tiers_from_dict(
    grid: Textgrid, *, items: Dict[str, str], index: int
) -> None:
    """Sets the given index of all tiers' label of given grid to given value"""
    for tier in grid.tierDict:
        grid.tierDict[tier].entryList[index] = replace_label(
            grid.tierDict[tier].entryList[index], lambda x: str(items[tier])
        )


def make_lowercase_entrylist(entryList: List[namedtuple]):
    """Get a copy of the entrylist where all labels are set to lowercase"""
    return [replace_label(entry, lambda x: x.lower()) for entry in entryList]
