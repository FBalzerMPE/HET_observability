"""Submodule to read the HET table."""

from typing import Literal

import numpy as np
from astropy.table import Table


def _get_other_hour_angles(
    het_table: Table, requested_angle: Literal[3, 4]
) -> np.ndarray:
    """Get the other hour angles from the HET table."""
    assert requested_angle in [
        3,
        4,
    ], f"Requested_angle must be 3 or 4, not {requested_angle}"
    # add ha3/ha4 for tracks of appropriate dec:
    #  dec boundaries of double-valued?
    d2min = -4.318553207530732
    d2max = 65.6814360000000
    # Not sure why it is this way around, just adopting it from before
    used_h_angle = "hour_angle_2" if requested_angle == 3 else "hour_angle_1"
    h_values = het_table[used_h_angle]
    d_values = het_table["dec"]

    mask = (d_values > d2min) & (d_values < d2max)
    new_hour_angles = np.where(mask, -h_values, -99)

    # Formerly, this was done as follows, I have refactored it to use vectorized operations:
    # new_ha_3 = np.array([-h if ((d > d2min) & (d < d2max)) else -99
    #    for h, d in zip(HET_TABLE["hour_angle_2"], HET_TABLE["dec"])])

    return new_hour_angles


def sanitize_het_table(het_table: Table) -> Table:
    """Read the HET opt tracking file and assign sensible column names.
    The columns are:
        ["dec", "total_time", "opt_az",
        "hour_angle_1", "hour_angle_2", "hour_angle_3", "hour_angle_4"]

    Returns
    -------
    Table
        The HET table.
    """
    old_names = [f"col{i}" for i in range(1, 6)]
    # I am not entirely sure what these columns are, but I think they are:
    new_names = ["dec", "total_time", "opt_az", "hour_angle_1", "hour_angle_2"]
    het_table.rename_columns(old_names, new_names)
    het_table["hour_angle_3"] = _get_other_hour_angles(het_table, 3)
    het_table["hour_angle_4"] = _get_other_hour_angles(het_table, 4)
    return het_table
