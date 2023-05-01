from __future__ import annotations

from typing import Set

from praatio.data_classes.textgrid import Textgrid
from praatio.data_classes.interval_tier import IntervalTier
from praatio.data_classes.point_tier import PointTier
from praatio.utilities.constants import Point

from dynamicfluency.helpers import split_pos_label, get_midpoint
from dynamicfluency.model_data import get_valid_tags

# This can be seen as a temporairy solution
BASE_VERBS = {"VBZ", "VBP", "VBD", "VB", "ROOT", "VC", "VE", "VP", "VERB"}
CLAUSE_VERBS = {"VBG", "VBN", "AUX", "MD", "VV"}


def label_contains_pos(lab: str, guard: Set[str]) -> bool:
    return any(pos in guard for pos in split_pos_label(lab, get_pos=True).split())


def validate_pos(pos_tier: IntervalTier, lang: str) -> bool:
    valid_tags = get_valid_tags(lang)
    return all(
        label_contains_pos(interval.label, valid_tags)
        for interval in pos_tier.entryList
        if interval.label
    )


def create_clause_point_tier(pos_tier: IntervalTier) -> PointTier:
    entryList = [
        Point(get_midpoint(interval), "")
        for interval in pos_tier.entryList
        if label_contains_pos(interval.label, CLAUSE_VERBS.union(BASE_VERBS))
    ]
    return PointTier(
        name="Syntactic Clauses",
        entryList=entryList,
        minT=pos_tier.minTimestamp,
        maxT=pos_tier.maxTimestamp,
    )


def create_phrase_point_tier(pos_tier: IntervalTier) -> PointTier:
    entryList = [
        Point(get_midpoint(interval), "")
        for interval in pos_tier.entryList
        if label_contains_pos(interval.label, BASE_VERBS)
    ]
    return PointTier(
        name="Syntactic Phrases",
        entryList=entryList,
        minT=pos_tier.minTimestamp,
        maxT=pos_tier.maxTimestamp,
    )


def make_syntax_grid(pos_tier: IntervalTier, lang: str) -> Textgrid:
    if not validate_pos(pos_tier, lang):
        raise ValueError("POS_tier contains unreadable pos labels")

    syntax_grid = Textgrid(pos_tier.minTimestamp, pos_tier.maxTimestamp)
    syntax_grid.addTier(create_clause_point_tier(pos_tier))
    syntax_grid.addTier(create_phrase_point_tier(pos_tier))
    return syntax_grid
