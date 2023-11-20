"""Submodule to read the visits table."""
from typing import TYPE_CHECKING

import numpy as np
from astropy.table import Table

if TYPE_CHECKING:
    from ...config import HTC_CONFIG


def _get_single_time_to_lose(het_entry: float, dark_entry: float) -> float:
    """Calculate the time to lose from the HETDEX entry and dark entry.
    It is the minimum of the het_entry and dark_entry."""
    if het_entry < dark_entry:
        return het_entry
    elif het_entry > dark_entry:
        return dark_entry
    else:
        return 0.0


def _get_time_to_lose(hetdex_visits: np.ndarray, dark_visits: np.ndarray) -> np.ndarray:
    """Calculate the time to lose from the HETDEX visits and dark visits."""
    return np.array(
        [
            _get_single_time_to_lose(het, dark)
            for het, dark in zip(hetdex_visits, dark_visits)
        ]
    )


def _subtract_hetdex_lose_time(visits_table: Table) -> Table:
    """Modify the visits table to subtract HETDEX time from dark and all visits."""
    # - Subtract as much from the "all" time as there is "dark" time.
    hetdex_visits = visits_table["visits_HETDEX"]
    dark_visits = visits_table["dark"]
    time_to_lose = _get_time_to_lose(hetdex_visits, dark_visits)
    visits_table["all"] -= time_to_lose
    visits_table["dark"] -= time_to_lose
    return visits_table


def _get_lst_step_size(visits_table: Table) -> float:
    """Calculate the LST step size from the visits table."""
    # calculate LST step size from data
    lst_data = visits_table["LST"]
    dall = lst_data[1:] - lst_data[0:-1]
    step_size = np.mean(dall)
    return step_size


def sanitize_visits_table(visits_table: Table, config: "HTC_CONFIG") -> Table:
    """Load the visits file for the given year and trimester.

    Returns
    -------
    Table
        The visits table.
    """
    if config.include_hetdex:
        visits_table = _subtract_hetdex_lose_time(visits_table)
    return visits_table
