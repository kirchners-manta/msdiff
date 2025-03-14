"""
Main file for the ionic conductivity calculation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..functions import calc_transport_numbers, find_linear_region, linear_fit
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

    # read data from file
    
    # determine number of columns in the file
    with open(args.file, "r", encoding="utf-8") as f:
        first_line = f.readline()
        n_columns = len(first_line.split(";"))
    
    # if 'avg' option is true, the file contains the average values and the standard deviation
    # the file can contain either just the total conductivity or all contributions
    
    # average but only total conductivity
    if args.avg and n_columns == 3:
        data = pd.read_csv(
            args.file,
            sep=";",
            skiprows=1,
            names=[
                "time",
                "total_eh",
                "total_eh_std",
            ],
        ).astype(float)
        
        # add columns for all contributions and set them to zero
        data["anion_self"] = data["cation_self"] = data["anion_cross"] = data["cation_cross"] = data["anion_cation"] = 0.0
        data["anion_self_std"] = data["cation_self_std"] = data["anion_cross_std"] = data["cation_cross_std"] = data["anion_cation_std"] = 0.0
    
    # average and all contributions
    elif args.avg and n_columns == 14:
        data = pd.read_csv(
            args.file,
            sep=";",
            skiprows=1,
            names=[
                "time",
                "anion_self",
                "anion_self_std",
                "cation_self",
                "cation_self_std",
                "anion_cross",
                "anion_cross_std",
                "cation_cross",
                "cation_cross_std",
                "anion_cation",
                "anion_cation_std",
                "total_eh",
                "total_eh_std",
                " ",
            ],
        ).astype(float)
        
    # not average and only total conductivity
    elif not args.avg and n_columns == 2:
        data = pd.read_csv(
            args.file,
            sep=";",
            skiprows=1,
            names=[
                "time",
                "total_eh",
            ],
        ).astype(float)
        
        # add columns for all contributions and set them to zero
        data["total_eh_std"] = 0.0
        data["anion_self"] = data["cation_self"] = data["anion_cross"] = data["cation_cross"] = data["anion_cation"] = 0.0
        data["anion_self_std"] = data["cation_self_std"] = data["anion_cross_std"] = data["cation_cross_std"] = data["anion_cation_std"] = 0.0
    
    elif not args.avg and n_columns == 8:
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
                "total_eh",
                " ",
            ],
        ).astype(float)

        # add standard deviation columns and set them to zero
        data["anion_self_std"] = data["cation_self_std"] = data["anion_cross_std"] = data["cation_cross_std"] = data["anion_cation_std"] = data["total_eh_std"] = 0.0

    # calculate total anion and cation conductivity
    data["anion_tot"] = data["anion_self"] + data["anion_cross"]
    data["anion_tot_std"] = np.sqrt(
        data["anion_self_std"] ** 2 + data["anion_cross_std"] ** 2
    )
    data["cation_tot"] = data["cation_self"] + data["cation_cross"]
    data["cation_tot_std"] = np.sqrt(
        data["cation_self_std"] ** 2 + data["cation_cross_std"] ** 2
    )
    data["total_ne"] = data["anion_self"] + data["cation_self"]
    data["total_ne_std"] = np.sqrt(
        data["anion_self_std"] ** 2 + data["cation_self_std"] ** 2
    )

    # sort columns
    data = data[
        [
            "time",
            "anion_self",
            "anion_self_std",
            "anion_cross",
            "anion_cross_std",
            "anion_tot",
            "anion_tot_std",
            "cation_self",
            "cation_self_std",
            "cation_cross",
            "cation_cross_std",
            "cation_tot",
            "cation_tot_std",
            "anion_cation",
            "anion_cation_std",
            "total_ne",
            "total_ne_std",
            "total_eh",
            "total_eh_std",
        ]
    ]

    # find linear region, based on EH conductivity
    (firststep, laststep) = find_linear_region(
        data[["time", "total_eh"]],
        args.tolerance,
    )

    # empty list to store the results
    result_list = []
    # list of contributions
    cols = [
        "anion_self",
        "anion_cross",
        "anion_tot",
        "cation_self",
        "cation_cross",
        "cation_tot",
        "anion_cation",
        "total_ne",
        "total_eh",
    ]

    # loop over all contributions
    for _, data_set in enumerate(cols):
        # select data for one molecule
        cond_data = data[["time", data_set, f"{data_set}_std"]]

        # calculate conductivity
        # if no linear region is found, the function is not called
        # and the results are set to zero
        if firststep != -1 and laststep != -1:
            cond, delta_cond, r2, npoints_fit = linear_fit(
                cond_data,
                firststep,
                laststep,
            )
        else:
            cond = 0.0
            delta_cond = 0.0
            r2 = 0.0
            npoints_fit = 0

        # summarize results in a list
        result_list.append(
            [data_set, cond, delta_cond, r2, firststep, laststep, npoints_fit]
        )

    # summarize results in a data frame
    results = pd.DataFrame(
        data=result_list,
        columns=[
            "contribution",
            "sigma",
            "delta_sigma",
            "r2",
            "t_start",
            "t_end",
            "n_data",
        ],
    ).astype(
        {
            "contribution": str,
            "sigma": float,
            "delta_sigma": float,
            "r2": float,
            "t_start": float,
            "t_end": float,
            "n_data": int,
        }
    )

    # calculate a posteriori quantities
    a_posteriori = calc_transport_numbers(results)

    # rename contributions in results for proper output
    results = results.replace(
        {
            "anion_self": "anion self",
            "anion_cross": "anion cross",
            "anion_tot": "anion total",
            "cation_self": "cation self",
            "cation_cross": "cation cross",
            "cation_tot": "cation total",
            "anion_cation": "anion-cation",
            "total_ne": "Nernst-Einstein",
            "total_eh": "Einstein-Helfand",
        }
    )

    print_results_to_stdout(results, a_posteriori)

    print_results_to_file(results, a_posteriori, args.output)

    return 0
