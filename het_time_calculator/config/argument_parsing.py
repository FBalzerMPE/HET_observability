"""Define how command line arguments are handled."""

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config_setup import HetTimeCalcConfig


def parse_args(config: "HetTimeCalcConfig") -> argparse.Namespace:
    """Parse command line arguments.

    Returns
    -------
        argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="HETDEX PI targets: LST time calculator"
    )
    parser.add_argument(
        "--trimester",
        type=int,
        default=config.trimester,
        choices=[1, 2, 3],
        help=f"Desired trimester number (1,2,3). (DEFAULT: {config.trimester}).",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=config.year,
        # TODO: Implement more years
        choices=[2019, 2020],
        help=f"The year of the observation.\nCurrently, only 2019 and 2020 are supported. (DEFAULT: {config.year}).",
    )
    parser.add_argument(
        "--include_HETDEX",
        action="store_true",
        default=config.include_hetdex,
        help=f"Include HETDEX fields? (DEFAULT: {config.include_hetdex}).)",
    )
    parser.add_argument(
        "--include_losses",
        action="store_true",
        default=config.include_losses,
        help=f"Include weather/PR/eng time losses? (DEFAULT: {config.include_losses}).",
    )
    parser.add_argument(
        "--setup_time",
        type=int,
        default=config.setup_time,
        help=f"The setup time anticipated for each observation (DEFAULT: {config.setup_time}).",
    )
    parser.add_argument(
        "--target_input_file",
        type=str,
        default=config.target_input_file,
        help=f"Location of the targets file (DEFAULT: '{config.target_input_file}').",
    )
    parser.add_argument(
        "--output_stem",
        type=str,
        default=config.target_output_stem,
        help=f"The output file stem (DEFAULT: '{config.target_output_stem}').",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Whether to print verbose output during calculations (DEFAULT: False).",
    )
    parser.add_argument(
        "-p",
        "--show_plot",
        action="store_true",
        default=False,
        help="Whether to open the plot after running (DEFAULT: False).",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        default=False,
        help="Whether to automatically overwrite existing files (DEFAULT: False).",
    )
    args, _ = parser.parse_known_args()
    return args
