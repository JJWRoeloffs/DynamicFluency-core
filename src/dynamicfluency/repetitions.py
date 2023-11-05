from __future__ import annotations

from typing import List

import nltk
from praatio.data_classes.interval_tier import IntervalTier

from dynamicfluency.helpers import entrylist_labels_to_string, split_pos_label


def make_repetitions_tier(
    pos_tier: IntervalTier,
    *,
    max_cache: int = 100,
    to_ignore: List[str] = [],
    name: str = "Repetitions",
) -> IntervalTier:
    cache = []
    repetitions_list = []

    for entry in pos_tier.entryList:
        if (
            (not entry.label)
            or (entry.label in to_ignore)
            or (split_pos_label(entry.label) in to_ignore)
        ):
            repetitions_list.append(entry)
            continue

        cache.insert(0, entry.label)
        if len(cache) > max_cache:
            cache.pop()

        try:
            repetitions = str(1 / cache.index(entry.label, 1))
        except ValueError:
            repetitions = "0"

        repetitions_list.append(entry._replace(label=repetitions))

    return pos_tier.new(name=name, entryList=repetitions_list)


def make_freqdist_tier(
    pos_tier: IntervalTier, *, to_ignore: List[str] = [], name: str = "FreqDist"
) -> IntervalTier:
    processed_entryList = [
        interval
        for interval in pos_tier.entryList
        if interval.label
        if not interval.label in to_ignore
        if not split_pos_label(interval.label) in to_ignore
    ]

    text = entrylist_labels_to_string(processed_entryList)
    fdist = nltk.FreqDist(text.split())
    freqdist_list = []

    for entry in pos_tier.entryList:
        if (
            (not entry.label)
            or (entry.label in to_ignore)
            or (split_pos_label(entry.label) in to_ignore)
        ):
            freqdist_list.append(entry)
            continue

        frequency = str(fdist.freq(entry.label))
        freqdist_list.append(entry._replace(label=frequency))

    return pos_tier.new(name=name, entryList=freqdist_list)
