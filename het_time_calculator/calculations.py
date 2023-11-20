"""Define the functions used to calculate the start and stop times for each target,
and the number of visits for each time.
"""

from typing import Dict, Literal, Optional, Tuple

import numpy as np
from astropy.table import Row, Table

from .config import HTC_CONFIG, HetTimeCalcConfig
from .util import Trimester


def _get_optimal_hour_angles(het_table: Table, dec: float) -> Dict[str, float]:
    """For the given dec, find the optimal start/stop times in LST
    i.e., find closest h_dec and get the HA values (1,2,3,4).

    Returns
    -------
    dict[str, float]
        The optimal hour angles for the given dec, mapped via their names,
        i.e., "hour_angle_1": optimal hour angle 1.
    """
    dec_diff = np.abs(het_table["dec"] - dec)
    min_index = np.argmin(dec_diff)
    hour_angles = [f"hour_angle_{i}" for i in range(1, 5)]
    optimal_hour_angles = {
        ha_key: het_table[ha_key][min_index] for ha_key in hour_angles
    }
    return optimal_hour_angles


def _is_on_track(ha_1: float, ha_2: float) -> bool:
    """Determine if the given hour angles are valid
    Returns
    -------
    bool
        True if the target is on the given track, False otherwise.
    """
    return all(np.abs(hour_angle) < 5 for hour_angle in [ha_1, ha_2])


def _calculate_ha_values(ha1, ha2) -> Dict[str, float]:
    """Calculate the min, max, midpoint, and total hour angles from the given hour angles."""
    hami = np.min([ha1, ha2])
    hama = np.max([ha1, ha2])
    hamid = hami + (hama - hami) / 2.0
    ha_total = hama - hami
    keys = ["min", "max", "mid", "total"]
    values = hami, hama, hamid, ha_total
    return dict(zip(keys, values))


def _issue_exptime_warning(
    ha_total, req_h, num_visits_requested, needed_visits, hour_angles, target_id
):
    print(" ")
    print(f"Target: {target_id}")
    ha_str = ", ".join(f"{k}: {v:.2f}" for k, v in hour_angles.items())
    print(f"Optimal hour angles: {ha_str}")
    print(f"Only {ha_total:.2f} h on the first track available.")
    print(f"You requested: {req_h:.2f} h per ({num_visits_requested:.0f}) visit")
    print("\tWARNING: that is a PROBLEM -- need more visits.")
    print(f"\tFor now you get {needed_visits:.0f} visits instead.")


def _get_requested_time_per_visit(
    target: Row, setup_time: float, n_visits=None
) -> float:
    """Calculate the requested visit time in hours."""
    # The total visit time in hours is needed to be compared to the hour angle
    if n_visits is None:
        n_visits = target["num_visits"]
    return (target["t_exp"] / n_visits + setup_time) / 3600


def _adjust_time_depending_on_trimester(time: float, trimester: Trimester) -> float:
    # For trimester 1, keep the time above 22 h
    if trimester == Trimester.FIRST:
        if time <= 22:
            return time + 24.0
    # for trimester 2, we keep 0-24  ####OLD: allow up to 32h, and take negatives +24
    elif trimester == Trimester.SECOND:
        if time > 25:
            return time - 24.0
        # TODO: This seems fishy (I think it should be < 1), but it's what the original code did
        if time < 2:
            return time + 24.0
    # for trimester 3, less than 12, send up to >24    #to 36 now
    elif trimester == Trimester.THIRD:
        if time < 12:
            return time + 24.0
        if time > 36:
            return time - 24.0
    else:
        raise (ValueError(f"Trimester {trimester} not recognized."))
    return time


def _add_start_stop_times_for_single_target(
    target: Row, track: Literal[1, 2], het_table: Table, config: HetTimeCalcConfig
):
    """Get the LST start and stop times for the given target and track.
    Returns -99, -99 if the target is not on the given track.
    """
    assert track in [1, 2], f"Requested track must be 1 or 2, not {track}"

    opt_ha = _get_optimal_hour_angles(het_table, target["dec"])

    has_to_check = (1, 2) if track == 1 else (3, 4)
    ha_1, ha_2 = (opt_ha[f"hour_angle_{i}"] for i in has_to_check)

    if not _is_on_track(ha_1, ha_2):
        return

    ha_values = _calculate_ha_values(ha_1, ha_2)

    requested_visit_time = _get_requested_time_per_visit(target, config.setup_time)
    needed_visits = target["num_visits"]

    # VERIFY! is there enough time for this requested exptime within each visit?
    if requested_visit_time > ha_values["total"]:
        # If the requested time is above the available one, more visits are needed
        needed_visits = int(1 + target["t_exp"] / 3600.0 / ha_values["total"])
        if config.is_verbose:
            _issue_exptime_warning(
                ha_values["total"],
                requested_visit_time,
                target["num_visits"],
                needed_visits,
                opt_ha,
                target["target_id"],
            )
        # Set the new necessary visit time
        requested_visit_time = _get_requested_time_per_visit(
            target, config.setup_time, needed_visits
        )

    # Use total time to extend on either side of this, optimal.
    ha_start = ha_values["mid"] - requested_visit_time / 2.0
    ha_stop = ha_values["mid"] + requested_visit_time / 2.0

    ra_h = target["ra"] / 15.0
    # combine with target RA to get LST start/stop
    lst_start = ra_h + ha_start
    lst_stop = ra_h + ha_stop
    lst_start = _adjust_time_depending_on_trimester(lst_start, config.trimester)
    lst_stop = _adjust_time_depending_on_trimester(lst_stop, config.trimester)
    target[f"lst_{track}_start"] = lst_start
    target[f"lst_{track}_stop"] = lst_stop
    target[f"track_{track}_visits"] = needed_visits


# Determine the LST times for each target


def add_target_start_stop_times(
    target_table: Table, het_table: Table, config: HetTimeCalcConfig
) -> Table:
    """Add the start and stop times for visibility for each target.

    The HET table is used to determine the optimal hour angles for each target,
    and the target table is modified to include the start and stop times for each target.

    The columns added to the visits table are called
        ["lst_1_start", "lst_1_stop", "lst_2_start", "lst_2_stop",
        "track_1_visits", "track_2_visits", "insufficient_coverage"]

    Here, the first columns indicate the target's start and stop times for
    the specified tracks,
    while the second columns indicate the number of visits needed to observe them,
    which is equal to Nvis if the time is available, or more if it is not.
    """
    # First, register the columns with their default values
    for colname in ["lst_1_start", "lst_1_stop", "lst_2_start", "lst_2_stop"]:
        target_table[colname] = -99.0
    target_table["track_1_visits"] = 0
    target_table["track_2_visits"] = 0

    for target in target_table:
        _add_start_stop_times_for_single_target(
            target, track=1, het_table=het_table, config=config
        )
        _add_start_stop_times_for_single_target(
            target, track=2, het_table=het_table, config=config
        )
    target_table["insufficient_coverage"] = (
        target_table["track_1_visits"] > target_table["num_visits"]
    ) & (target_table["track_2_visits"] > target_table["num_visits"])
    return target_table


def _add_visit_counts_for_single_time(
    visit_row: Row, targets: Table
) -> Tuple[int, int, int]:
    """Calculate the total number of east, west, or single track visits for a given time."""
    time = visit_row["LST"]
    t_1_mask = targets["track_1_visits"] > 0
    t_2_mask = targets["track_2_visits"] > 0
    t_1_time_mask = (targets[f"lst_1_start"] < time) & (time < targets[f"lst_1_stop"])
    t_2_time_mask = (targets[f"lst_2_start"] < time) & (time < targets[f"lst_2_stop"])
    # Two times, east: All targets that have both tracks available and are in range for the given time
    east_mask = t_1_mask & t_2_mask & t_1_time_mask
    west_mask = t_1_mask & t_2_mask & t_2_time_mask
    single_mask_1 = t_1_mask & ~t_2_mask & t_1_time_mask
    single_mask_2 = ~t_1_mask & t_2_mask & t_2_time_mask
    # Opposed to how it was done before, I am using the visits prescribed to the target instead of the requested
    # ones (which were done using targets[Nvis])
    single_count = (
        targets[single_mask_1]["track_1_visits"].sum()
        + targets[single_mask_2]["track_2_visits"].sum()
    )
    visit_row["east_tracks"] = targets[east_mask]["track_1_visits"].sum()
    visit_row["west_tracks"] = targets[west_mask]["track_2_visits"].sum()
    visit_row["single_tracks"] = single_count


def add_visit_counts(visits_table: Table, target_table: Table) -> Table:
    """Add the visit counts, that is the count of targets that can be observed with both
    east and west tracks, and the counts for the targets which can only be observed via single
    tracks.

    The columns added to the visits table are called
        ["east_tracks", "west_tracks", "single_tracks"]
    """
    # First register the columns with their default values
    for colname in ["east_tracks", "west_tracks", "single_tracks"]:
        visits_table[colname] = 0

    # Then calculate the values
    for visit_entry in visits_table:
        _add_visit_counts_for_single_time(visit_entry, target_table)
    return visits_table


def perform_all_calculations(
    config: Optional[HetTimeCalcConfig] = None,
) -> Tuple[Table, Table]:
    """Perform the calculations get the enriched target and visits tables."""
    if config is None:
        config = HTC_CONFIG

    visits_table = config.get_visits_table()
    target_table = config.get_target_table()
    het_table = config.get_het_table()

    target_table = add_target_start_stop_times(target_table, het_table, config)
    visits_table = add_visit_counts(visits_table, target_table)
    return target_table, visits_table
