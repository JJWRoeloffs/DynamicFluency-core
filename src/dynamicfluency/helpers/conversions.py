from __future__ import annotations

from itertools import chain

from praatio.data_classes.textgrid_tier import TextgridTier

from .textgridtier_extensions import replace_label


def split_pos_label(pos_label: str, *, get_pos: bool = False) -> str:
    """The lemma split from the full POS tag label.
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
    lemmas_and_tags = chain(*[lemma.split(" ") for lemma in split])
    lemmas = [lemma for i, lemma in enumerate(lemmas_and_tags) if (i % 2) == index]
    return join.join(lemmas)


def pos_tier_to_lemma_tier(
    pos_tier: TextgridTier, name: str = "Lemmas"
) -> TextgridTier:
    """Makes a lemma tier out of a pos_tagging made pos_tier"""
    lemma_list = [replace_label(entry, split_pos_label) for entry in pos_tier.entryList]
    return pos_tier.new(name=name, entryList=lemma_list)
