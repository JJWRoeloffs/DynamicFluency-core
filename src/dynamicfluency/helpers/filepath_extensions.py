from __future__ import annotations

from pathlib import Path
from typing import List


def get_local_glob(*paths: str, glob: str) -> List[Path]:
    """small helper function to not have to repeat this over and over again.

    The resolve is needed to be able to pass the path around as a string,
    which is needed for dependencies"""
    return list(Path().resolve().joinpath(*paths).glob(glob))
