"""
Main file for the ionic conductivity calculation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..functions import find_cond_region, get_conductivity
from .output import print_results_to_file, print_results_to_stdout


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
            "total",
        ],
    )

    data["anion"] = data["anion_self"] + data["anion_cross"]
    data["cation"] = data["cation_self"] + data["cation_cross"]

    # drop old anions and cations columns
    data = data.drop(
        columns=["anion_self", "cation_self", "anion_cross", "cation_cross"]
    )
    # sort columns as anion, cation, anion_cation, total
    data = data[["time", "anion", "cation", "anion_cation", "total"]]

    result_list = []
    for i, data_set in enumerate(data.columns[1:]):
        # select data for one molecule
        cond_data = data[["time", data_set]]
        # find linear region
        (firststep, laststep) = find_cond_region(
            cond_data,
            tskip=0.10,
            tol=0.1,
        )
        # calculate conductivity
        # if no linear region is found, the function is not called
        # and the results are set to zero
        if firststep != -1 and laststep != -1:
            cond, delta_cond, r2, npoints_fit = get_conductivity(
                cond_data,
                firststep,
                laststep,
            )
        else:
            cond = 0.0
            delta_cond = 0.0
            r2 = 0.0
            npoints_fit = 0
        # print(
        #     f"{data_set:<15} {firststep:<10} {laststep:<10} {cond:.4f} +- {delta_cond:.4f} S/m {f'r2 = {r2:.4f}':<10}"
        # )

        # summarize results in a list
        result_list.append(
            [data_set, cond, delta_cond, r2, firststep, laststep, npoints_fit]
        )

    # summarize results in a data frame
    results = pd.DataFrame(
        data=result_list,
        columns=[
            "Contribution",
            "sigma",
            "delta_sigma",
            "r2",
            "t_start",
            "t_end",
            "n_data",
        ],
    )

    print_results_to_stdout(results)

    # Rename columns for proper output
    results = results.rename(
        columns={
            "sigma": "sigma / S*m^-1",
            "delta_sigma ": "delta_sigma / S*m^-1",
            "t_start": "t_start / ps",
            "t_end": "t_end / ps",
            "n_data": "n_data_fit",
        }
    )
    print_results_to_file(results, args.output)

    return 0
