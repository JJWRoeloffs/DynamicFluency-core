from __future__ import annotations

from itertools import chain

from praatio.data_classes.textgrid_tier import TextgridTier
from praatio.utilities.constants import Interval

from .textgridtier_extensions import replace_label


def get_midpoint(interval: Interval) -> float:
    return (interval.start + interval.end) / 2


def split_pos_label(pos_label: str, *, get_pos: bool = False) -> str:
    """The word_form split from the full POS tag label.
    This label can have multiple words causing complication.
    It determines the splits by "_" and " ", the form "part_tag part_tag part_tag"
    Example:
    "is_VB" -> "is",
    "is_VB n't_RB" -> "isn't"
    Example for get_pos=True:
    "is_VB" -> "VB",
    "is_VB n't_RB" -> "VB RB"

    """
    index = 1 if get_pos else 0
    join = " " if get_pos else ""

    split = pos_label.split("_")
    forms_and_tags = chain(*[word_form.split(" ") for word_form in split])
    forms = [form for i, form in enumerate(forms_and_tags) if (i % 2) == index]
    return join.join(forms)


def pos_tier_to_word_form_tier(
    pos_tier: TextgridTier, name: str = "WordForms"
) -> TextgridTier:
    """Makes a word_form tier out of a pos_tagging made pos_tier"""
    word_form_list = [
        replace_label(entry, split_pos_label) for entry in pos_tier.entryList
    ]
    return pos_tier.new(name=name, entryList=word_form_list)
