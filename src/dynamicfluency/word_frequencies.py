from __future__ import annotations

import sqlite3
from typing import List, Optional

from praatio.data_classes.textgrid import Textgrid
from praatio.data_classes.interval_tier import IntervalTier

from dynamicfluency.helpers import (
    set_all_tiers_static,
    set_all_tiers_from_dict,
    split_pos_label,
)


def get_column_names(cursor: sqlite3.Cursor, *, table_name: str) -> List[str]:
    """Returns all the column names from the specified table"""
    cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO(?);", [table_name])
    return [name[0] for name in cursor.fetchall()]


def make_empty_frequency_grid(
    *,
    cursor: sqlite3.Cursor,
    table_name: str,
    base_tier: IntervalTier,
    columns: Optional[List[str]] = None,
) -> Textgrid:
    """Makes an "empty" frequency grid.
    This is a grid that has all the tiers initialised according to the column names of the databse,
    but does not have any values in those tiers, all of them being copies from the base.
    """
    if columns is None:
        columns = get_column_names(cursor, table_name=table_name)
    frequency_grid = Textgrid()
    for name in columns:
        tier = base_tier.new(name=name)
        frequency_grid.addTier(tier)
    return frequency_grid


def set_labels_from_db(
    *,
    cursor: sqlite3.Cursor,
    grid: Textgrid,
    table_name: str,
    word_form: str,
    index: int,
) -> None:
    """Sets the tiers of a textgrid with one tier for every databse column to their respecive entries at an index"""
    word_form_parts = word_form.split("'")
    set_all_tiers_static(grid, item="", index=index)

    for part in word_form_parts:
        cursor.execute(
            f"SELECT DISTINCT * FROM {table_name} WHERE LOWER(WordForm) LIKE LOWER((?));",
            [part],
        )

        try:
            row = cursor.fetchall()[0]
        except IndexError:
            set_all_tiers_static(grid, item="MISSING", index=index)
            return
        else:
            set_all_tiers_from_dict(grid, items=row, index=index, append=True)


def create_frequency_grid(
    word_form_tier: IntervalTier,
    *,
    cursor: sqlite3.Cursor,
    table_name: str,
    to_ignore: Optional[List[str]] = None,
    columns: Optional[List[str]] = None,
) -> Textgrid:
    """Create frequency grid from database connection"""
    to_ignore = [] if to_ignore is None else to_ignore

    frequency_grid = make_empty_frequency_grid(
        cursor=cursor, table_name=table_name, base_tier=word_form_tier, columns=columns
    )

    for i, entry in enumerate(word_form_tier.entryList):
        if (
            (not entry.label)
            or (entry.label in to_ignore)
            or (split_pos_label(entry.label) in to_ignore)
        ):
            set_all_tiers_static(frequency_grid, item="", index=i)
        else:
            set_labels_from_db(
                cursor=cursor,
                grid=frequency_grid,
                table_name=table_name,
                word_form=entry.label,
                index=i,
            )

    return frequency_grid
