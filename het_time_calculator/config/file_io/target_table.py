from typing import TYPE_CHECKING

from astropy.table import Table

if TYPE_CHECKING:
    from ..config_setup import HetTimeCalcConfig


def sanitize_target_table(targets: Table, config: "HetTimeCalcConfig") -> Table:
    """Sanitize the target table, unifying the column names."""

    # Alternative column names, unified to our standard
    if "ID" in targets.colnames:
        targets.rename_column("ID", "target_id")
    if "exptime" in targets.colnames:
        targets.rename_column("exptime", "t_exp")
    if "Nvis" in targets.colnames:
        targets.rename_column("Nvis", "num_visits")

    lower_case_columns = [col.lower() for col in targets.colnames]
    # Register the number of visits as 1 if it is not present
    if "num_visits" not in lower_case_columns:
        targets["num_visits"] = 1
        if config.is_verbose:
            print(
                "No num_visits column found, assuming that each target should be observed once."
            )
    # Ensure that the column names are lowercase as we'd expect them to be
    required_columns = ["target_id", "ra", "dec", "t_exp"]
    for col in required_columns:
        assert col in lower_case_columns, f"Column {col} not found in target table."
    actual_colnames = [
        col for col in targets.colnames if col.lower() in required_columns
    ]
    targets.rename_columns(actual_colnames, [col.lower() for col in actual_colnames])
    return targets
