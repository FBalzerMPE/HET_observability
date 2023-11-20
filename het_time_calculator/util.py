from enum import Enum
from pathlib import Path

import numpy as np

# The following are the fractions of time lost to weather, PR, and engineering, which are currently unused.

# time lost assumptions: 0.056(PR), 0.?(ENG), 0.3(WEATHER,monthly)
#    PR fraction is calculated AFTER accounting for weathered out nights
FRACTIONS_WEATHER_LOST = np.array(
    [0.359, 0.337, 0.379, 0.335, 0.335, 0.339, 0.499, 0.428, 0.476, 0.314, 0.246, 0.346]
)
#       Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec
FRACTION_PR_LOST = 0.056
# engr time is only during bright, and is 10%:
FRACTION_ENG_LOST = 0.10

# merge weather+PR, monthly array
FRACTION_GOOD_TIME = (1.0 - FRACTIONS_WEATHER_LOST) * (1.0 - FRACTION_PR_LOST)


def ask_overwrite(fpath: Path) -> bool:
    """Ask the user if they want to overwrite the given file.
    If the file exists, ask the user if they want to overwrite it.
    If the user answers 'y', return True, otherwise False.
    If the file does not exist, return True.
    """
    if fpath.exists():
        answer = input(f"{fpath} already exists. Do you want to overwrite? [y/n] ")
        # After 5 unsuccessful tries, skip overwriting
        for _ in range(5):
            if answer.lower() in ["y", "yes"]:
                return True
            elif answer.lower() in ["n", "no"]:
                return False
            answer = input("Please answer with 'y' or 'n'.")
        return False
    return True


class Trimester(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, int):
            return self.value == __value
        return super().__eq__(__value)
