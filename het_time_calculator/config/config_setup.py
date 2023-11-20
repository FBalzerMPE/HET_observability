"""Contains the setup for the configuration settings of the
HET time calculator, as well as the configuration object itself.

The configuration object is called HTC_CONFIG and is used throughout the
code to access the configuration settings, which can also be changed
via a command line call."""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Tuple

from astropy.io.ascii import read as ascii_read
from astropy.table import Table
from matplotlib.figure import Figure

from ..util import Trimester, ask_overwrite
from .argument_parsing import parse_args
from .file_io import sanitize_het_table, sanitize_target_table, sanitize_visits_table


@dataclass
class HetTimeCalcConfig:
    """The configuration parameters for the HETDEX time calculator."""

    trimester: Trimester = 1
    "The trimester number (1,2,3)"

    year: int = 2020
    "The year of the observation"

    include_hetdex: bool = True
    "Include HETDEX fields for the calculations? (True)"

    include_losses: bool = True
    "Include weather/PR/eng time losses? (True)"

    setup_time: int = 300
    "The estimated setup time for each target in seconds (300)"

    target_input_file: str = "example_targets.dat"
    "Location of the targets file (example_targets.dat)"

    target_output_stem: str = "output/LST_visits_PI"
    "The stem and path for the output files (output/LST_visits_PI)"

    is_verbose: bool = False
    "Print verbose output? (True)"

    show_plot: bool = False
    "Show the plot after running? (True)"

    overwrite_existing: bool = False
    "Automatically overwrite existing files? (False)"

    def __post_init__(self):
        for fpath in [
            self._fpath_visit_file,
            self._fpath_het_table,
        ]:
            assert fpath.exists(), f"File {fpath} not found."

    @property
    def _base_path(self) -> Path:
        # The directory the het_time_calculator lives in
        return Path(__file__).parent.parent.parent

    @property
    def _fpath_visit_file(self) -> Path:
        """The path to the visits file."""
        fpath = self._base_path.joinpath(
            f"data/allvisits_byLST_wHETDEX_{self.year}-{self.trimester}.dat"
        )
        return fpath

    @property
    def _fpath_target_input_file(self) -> Path:
        """The path to the target file."""
        return Path(self.target_input_file)

    @property
    def _fpath_het_table(self) -> Path:
        """The path to the HET observation optical tracking file."""
        return self._base_path.joinpath("data/HET_opt_tracking.txt")

    @property
    def lst_offset(self) -> int:
        """The offset to use for plotting."""
        if self.trimester == Trimester.FIRST:
            return 20
        elif self.trimester == Trimester.SECOND:
            return 2
        elif self.trimester == Trimester.THIRD:
            return 12
        raise ValueError(f"Trimester {self.trimester} not recognized.")

    @property
    def x_axis_limits(self) -> Tuple[float, float]:
        """The limits for the x-axis."""
        return (-0.5 + self.lst_offset, 24.5 + self.lst_offset)

    @property
    def _fpath_plot(self) -> Path:
        """The path to the overview plot file."""
        return Path(
            f"{self.target_output_stem}_{self.year}_{self.trimester}_overview.pdf"
        )

    @property
    def _fpath_target_output(self) -> Path:
        """The path to the output target file."""
        return Path(f"{self.target_output_stem}_targets.dat")

    @classmethod
    def from_args(cls) -> "HetTimeCalcConfig":
        """Create a HetTimeCalcConfig from the command line arguments."""
        args = parse_args(cls)
        return cls(
            trimester=Trimester(args.trimester),
            year=args.year,
            include_hetdex=args.include_HETDEX,
            include_losses=args.include_losses,
            setup_time=args.setup_time,
            target_input_file=args.target_input_file,
            target_output_stem=args.output_stem,
            is_verbose=args.verbose,
            show_plot=args.show_plot,
            overwrite_existing=args.overwrite,
        )

    def get_het_table(self) -> Table:
        """Read and sanitize the HET table."""
        het_table: Table = ascii_read(self._fpath_het_table)
        het_table = sanitize_het_table(het_table)
        return het_table

    def get_target_table(self) -> Table:
        """Read the target table."""
        # This is its own function since we might add some sanitization later
        target_table: Table = ascii_read(HTC_CONFIG._fpath_target_input_file)
        return sanitize_target_table(target_table, self)

    def get_visits_table(self) -> Table:
        """Read and sanitize the visits table."""
        visits_table: Table = ascii_read(self._fpath_visit_file)
        visits_table = sanitize_visits_table(visits_table, self)
        return visits_table

    def write_output_file(self, targets: Table):
        """Write the output file with the calculated visit times."""
        fpath = self._fpath_target_output
        if self.overwrite_existing or ask_overwrite(fpath):
            targets.write(fpath, format="ascii.fixed_width_two_line", overwrite=True)
            if self.is_verbose:
                print(f"Output file written to '{fpath}'.")
        else:
            if self.is_verbose:
                print(f"Output file not written.")

    def save_plot(self, fig: Figure):
        """Save the plot."""
        fpath = self._fpath_plot
        if self.overwrite_existing or ask_overwrite(fpath):
            fig.savefig(fpath, bbox_inches="tight", dpi=300)
            if self.is_verbose:
                print(f"Plot saved to '{fpath}'.")
        else:
            if self.is_verbose:
                print(f"Plot not saved.")


HTC_CONFIG = HetTimeCalcConfig.from_args()
