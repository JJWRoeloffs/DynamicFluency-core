from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from praatio.utilities.constants import Interval
from praatio.data_classes.interval_tier import IntervalTier


class AeneasIntervaltier(IntervalTier):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @staticmethod
    def force_entrylist_validity(entryList: List[Interval]) -> List[Interval]:
        entryList.sort()

        validated_entryList = []
        for i, entry in enumerate(entryList):
            start = entry.start
            end = entry.end

            try:
                previous = validated_entryList[i - 1]
            except IndexError:
                previous = None

            if previous is not None and previous.start >= start:
                start = previous.start + 0.00001
            if start >= end:
                end = start + 0.00001

            validated_entryList.append(
                Interval(start=start, end=end, label=entry.label)
            )

        return validated_entryList

    @classmethod
    def from_json(
        cls, alignments: Dict, name: str, *, force_validity: bool = True
    ) -> AeneasIntervaltier:
        entryList = []
        for fragment in alignments["fragments"]:
            entry = Interval(
                start=float(fragment["begin"]),
                end=float(fragment["end"]),
                label=" ".join(fragment["lines"]),
            )
            entryList.append(entry)

        if force_validity:
            entryList = cls.force_entrylist_validity(entryList)

        return cls(name=name, entryList=entryList)


def aeneas_tier_from_file(
    file: Path, name: str, *, force_validity: bool = True
) -> AeneasIntervaltier:
    with file.open("r") as f:
        alignment_dict = json.load(f)
    return AeneasIntervaltier.from_json(
        alignment_dict, name, force_validity=force_validity
    )
