"""
Main script for msdiff.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..functions import (calc_Hummer_correction, find_linear_region,
                         perform_linear_regression)


def diffusion_coefficient(args: argparse.Namespace) -> int:

    # read the file and drop derivative column
    data = pd.read_csv(args.file, sep=";", skiprows=1, names=["time", "msd", "derivative"])
    data = data.drop(columns=["derivative"])

    print(len(data))

    firststep = find_linear_region(data, args.tolerance)

    print(firststep)

    return 0
