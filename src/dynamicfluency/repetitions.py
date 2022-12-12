from __future__ import annotations

import glob
import argparse
from typing import List

import nltk
from praatio import textgrid as tg
from praatio.data_classes.textgrid_tier import TextgridTier

from dynamicfluency.helpers import entrylist_labels_to_string


def make_repetitions_tier(
    pos_tier: TextgridTier,
    *,
    max_cache: int = 100,
    to_ignore: List[str] = [],
    name: str = "Repetitions",
) -> TextgridTier:

    cache = []
    repetitions_list = []

    for entry in pos_tier.entryList:
        if (not entry.label) or (entry.label in to_ignore):
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
    pos_tier: TextgridTier, *, to_ignore: List[str] = [], name: str = "FreqDist"
) -> TextgridTier:
    nltk.download("punkt", quiet=True, halt_on_error=True)

    text = entrylist_labels_to_string(pos_tier.entryList, to_ignore=to_ignore)
    fdist = nltk.FreqDist(nltk.word_tokenize(text))
    freqdist_list = []

    for entry in pos_tier.entryList:
        if (not entry.label) or (entry.label in to_ignore):
            freqdist_list.append(entry)
            continue

        frequency = str(fdist.freq(entry.label))
        freqdist_list.append(entry._replace(label=frequency))

    return pos_tier.new(name=name, entryList=freqdist_list)
