from __future__ import annotations

from typing import Callable, List, Dict
from collections import namedtuple

from praatio.data_classes.textgrid import Textgrid


def replace_label(entry: namedtuple, f: Callable) -> namedtuple:
    """Returns a new namedtuple with the "label" attribute changed according to passed function."""
    return entry._replace(label=f(entry.label))


def entrylist_labels_to_string(
    entryList: List[namedtuple], *, to_ignore: List[str] = []
) -> str:
    """Make a single space-seperated string, out of the labels of an entryList
    Useful to make a "sentence" out of the words in the tier."""
    return " ".join(
        [
            entry.label
            for entry in entryList
            if entry.label and (not entry.label in to_ignore)
        ]
    )


def set_all_tiers_static(grid: Textgrid, *, item: str, index: int) -> None:
    """Sets the given index of all tiers' label of given grid to given value"""
    for tier in grid.tierDict:
        grid.tierDict[tier].entryList[index] = (
            grid.tierDict[tier].entryList[index]._replace(label=item)
        )


def set_all_tiers_from_dict(
    grid: Textgrid,
    *,
    items: Dict[str, str],
    index: int,
    append: bool = False,
) -> None:
    """Sets the given index of all tiers' label of given grid to given value"""
    function = (
        (lambda y: lambda x: y)
        if not append
        else (lambda y: lambda x: str(" ".join([str(x), str(y)]).strip()))
    )
    for tier in grid.tierDict:
        if items[tier] is None:
            continue
        grid.tierDict[tier].entryList[index] = replace_label(
            grid.tierDict[tier].entryList[index], function(items[tier])
        )


def make_lowercase_entrylist(entryList: List[namedtuple]):
    """Get a copy of the entrylist where all labels are set to lowercase"""
    return [replace_label(entry, str.lower) for entry in entryList]
