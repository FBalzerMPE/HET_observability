from typing import Tuple

import matplotlib.pyplot as plt
from astropy.table import Table
from matplotlib import rc
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MultipleLocator

from .config import HTC_CONFIG

rc("font", **{"family": "serif", "serif": ["Computer Modern Roman"], "size": 20})
rc("text", usetex=True)


def _format_ticks_to_represent_hours(value, tick_number) -> str:
    # This function returns the label for each tick on the x-axis.
    # If the value is greater than 24, it subtracts 24 from it.
    return f"{value:.0f}" if value <= 24 else value - 24


def _add_labels_and_descriptions(ax: Axes):
    """Set pretty labels and texts for the ax"""
    hetdex_info_text = (
        "Subtracting HETDEX allocations."
        if HTC_CONFIG.include_hetdex
        else "Not including HETDEX fields."
    )
    ax.set_title(
        f"PI target visits for {HTC_CONFIG.year}-{HTC_CONFIG.trimester}\n{hetdex_info_text}"
    )
    ax.set_ylabel(r"$N$ visits (including weather/etc)")
    ax.set_xlabel(r"LST [h]")
    colored_labels = {
        "Single tracks (N/S)": "blue",
        "West tracks": "red",
        "East tracks": "green",
    }
    for i, (label, color) in enumerate(colored_labels.items()):
        y = 64.5 - i * 4
        ax.text(0 + HTC_CONFIG.lst_offset, y, label, color=color, alpha=0.8)
    ax.grid(True, which="minor", axis="y", alpha=0.2)
    ax.grid(True, which="major", axis="y", alpha=0.7)


def setup_visit_plot() -> Tuple[Figure, Axes]:
    """Set up the plot for the visit showcase,
    where the x-axis displays the 24 h of LST, and the y-axis the number of visits
    for each of the times."""
    # - Set up figure and axes
    fig, ax = plt.subplots(figsize=(13, 6))
    plt.subplots_adjust(wspace=0.25, hspace=0)
    ax.set_xlim(*HTC_CONFIG.x_axis_limits)
    ax.set_ylim(0, 70)
    ax.tick_params(axis="both", which="major", labelsize=16)
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_major_locator(MultipleLocator(6))
    # Create a FuncFormatter object based on the format_func function.
    formatter = FuncFormatter(_format_ticks_to_represent_hours)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(25))
    _add_labels_and_descriptions(ax)
    return fig, ax


def _plot_track_histograms(ax: Axes, visit_table: Table):
    x_vals = visit_table["LST"]
    y_east, y_west = visit_table["east_tracks"], visit_table["west_tracks"]
    y_single = visit_table["single_tracks"]

    ax.fill(x_vals, y_single, color="blue", lw=0, alpha=0.8)
    ax.fill(x_vals, y_east, color="red", lw=0, alpha=0.3)
    ax.fill(x_vals, y_west, color="green", lw=0, alpha=0.3)


def _plot_visit_curves(ax: Axes, visit_table: Table):
    """Plot the visit times on the given ax."""
    x_vals = visit_table["LST"]
    y_all, y_dark, y_gray = (
        visit_table["all"],
        visit_table["dark"],
        visit_table["gray"] + visit_table["dark"],
    )
    ax.plot(x_vals, y_all, color="black", lw=3, label="All (bright+gray+dark)")
    ax.plot(x_vals, y_dark, color="black", lw=1, label="Dark")
    ax.plot(x_vals, y_gray, color="grey", lw=2, label="Gray (gray+dark)")


def plot_visit_histograms(ax: Axes, visit_table: Table):
    """Plot the visit histograms on the given ax."""
    _plot_visit_curves(ax, visit_table)
    _plot_track_histograms(ax, visit_table)
    ax.legend(loc="upper right", fontsize=15)
