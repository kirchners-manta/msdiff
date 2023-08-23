"""
Main file for the ionic conductivity calculation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..functions import find_cond_region, get_conductivity


def conductivity(args: argparse.Namespace) -> int:
    """Function to calculate the ionic conductivity.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed command line arguments

    Returns
    -------
    int
        Exit code of the program
    """

    data = pd.read_csv(
        args.file,
        sep=";",
        skiprows=1,
        names=[
            "time",
            "anion_self",
            "cation_self",
            "anion_cross",
            "cation_cross",
            "anion_cation",
            "total  ",
        ],
    )

    data["anion_complete"] = data["anion_self"] + data["anion_cross"]
    data["cation_complete"] = data["cation_self"] + data["cation_cross"]

    # drop old anions and cations columns
    data = data.drop(
        columns=["anion_self", "cation_self", "anion_cross", "cation_cross"]
    )
    # sort columns as anion, cation, anion_cation, total

    for i, data_set in enumerate(data.columns[1:]):
        # select data for one molecule
        cond_data = data[["time", data_set]]
        # find linear region
        (firststep, laststep) = find_cond_region(
            cond_data,
            tskip=0.1,
            tol=0.10,
        )
        # calculate conductivity
        # if no linear region is found, the function is not called
        # and the results are set to zero
        if firststep != -1 and laststep != -1:
            cond, delta_cond, r2 = get_conductivity(
                cond_data,
                firststep,
                laststep,
            )
        else:
            cond = 0.0
            delta_cond = 0.0
            r2 = 0.0

        print(
            f"{data_set}:\t {laststep}, {firststep}, {cond:.4f} +- {delta_cond:.4f} S/m, r2 = {r2:.4f}"
        )

    return 0
