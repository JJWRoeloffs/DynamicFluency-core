import csv

from pathlib import Path
from typing import List

DATAFILE = Path(__file__).parent.joinpath("valid_pos_tags.csv")


def get_valid_tags() -> List:
    with DATAFILE.open("r") as f:
        tags = csv.reader(f)
        return list(*tags)
