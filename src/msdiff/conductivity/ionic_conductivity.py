"""
Main file for the ionic conductivity calculation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import numpy as np

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
            "total_eh",
            " ",
        ],
    )

    data["anion_tot"] = data["anion_self"] + data["anion_cross"]
    data["cation_tot"] = data["cation_self"] + data["cation_cross"]
    data["total_ne"] = data["anion_self"] + data["cation_self"]

    # drop old anions and cations columns
    data = data.drop(
        columns=[
            "anion_cross",
            "cation_cross",
            " ",
        ]
    )
    # sort columns as anion, cation, anion_cation, total
    data = data[
        [
            "time",
            "anion_self",
            "anion_tot",
            "cation_self",
            "cation_tot",
            "anion_cation",
            "total_ne",
            "total_eh",
        ]
    ]

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

    # get the index of the total_eh and total_ne columns
    total_eh_ind = results.index[results["Contribution"] == "total_eh"][0]
    total_ne_ind = results.index[results["Contribution"] == "total_ne"][0]
    cat_self_ind = results.index[results["Contribution"] == "cation_self"][0]
    an_self_ind = results.index[results["Contribution"] == "anion_self"][0]
    cat_tot_ind = results.index[results["Contribution"] == "cation_tot"][0]
    an_tot_ind = results.index[results["Contribution"] == "anion_tot"][0]

    # calculate a posteriori quantities
    ionicity = results.loc[total_eh_ind, "sigma"] / results.loc[total_ne_ind, "sigma"]

    delta_ionicity = np.sqrt(
        (results.loc[total_eh_ind, "delta_sigma"] / results.loc[total_ne_ind, "sigma"])
        ** 2
        + (
            results.loc[total_eh_ind, "sigma"]
            * results.loc[total_ne_ind, "delta_sigma"]
            / results.loc[total_ne_ind, "sigma"] ** 2
        )
        ** 2
    )

    sigma_an_cross = (
        results.loc[an_tot_ind, "sigma"] - results.loc[an_self_ind, "sigma"]
    )

    delta_sigma_an_cross = np.sqrt(
        results.loc[an_tot_ind, "delta_sigma"] ** 2
        + results.loc[an_self_ind, "delta_sigma"] ** 2
    )

    sigma_cat_cross = (
        results.loc[cat_tot_ind, "sigma"] - results.loc[cat_self_ind, "sigma"]
    )

    delta_sigma_cat_cross = np.sqrt(
        results.loc[cat_tot_ind, "delta_sigma"] ** 2
        + results.loc[cat_self_ind, "delta_sigma"] ** 2
    )

    t_self_an = results.loc[an_self_ind, "sigma"] / results.loc[total_ne_ind, "sigma"]

    delta_t_self_an = np.sqrt(
        (results.loc[an_self_ind, "delta_sigma"] / results.loc[total_ne_ind, "sigma"])
        ** 2
        + (
            results.loc[an_self_ind, "sigma"]
            * results.loc[total_ne_ind, "delta_sigma"]
            / results.loc[total_ne_ind, "sigma"] ** 2
        )
        ** 2
    )

    t_self_cat = results.loc[cat_self_ind, "sigma"] / results.loc[total_ne_ind, "sigma"]

    delta_t_self_cat = np.sqrt(
        (results.loc[cat_self_ind, "delta_sigma"] / results.loc[total_ne_ind, "sigma"])
        ** 2
        + (
            results.loc[cat_self_ind, "sigma"]
            * results.loc[total_ne_ind, "delta_sigma"]
            / results.loc[total_ne_ind, "sigma"] ** 2
        )
        ** 2
    )

    t_an = results.loc[an_tot_ind, "sigma"] / results.loc[total_eh_ind, "sigma"]

    delta_t_an = np.sqrt(
        (results.loc[an_tot_ind, "delta_sigma"] / results.loc[total_eh_ind, "sigma"])
        ** 2
        + (
            results.loc[an_tot_ind, "sigma"]
            * results.loc[total_eh_ind, "delta_sigma"]
            / results.loc[total_eh_ind, "sigma"] ** 2
        )
        ** 2
    )

    t_cat = results.loc[cat_tot_ind, "sigma"] / results.loc[total_eh_ind, "sigma"]

    delta_t_cat = np.sqrt(
        (results.loc[cat_tot_ind, "delta_sigma"] / results.loc[total_eh_ind, "sigma"])
        ** 2
        + (
            results.loc[cat_tot_ind, "sigma"]
            * results.loc[total_eh_ind, "delta_sigma"]
            / results.loc[total_eh_ind, "sigma"] ** 2
        )
        ** 2
    )

    # put the a posteriori quantities to a new data frame
    a_posteriori = pd.DataFrame(
        data=[
            [
                ionicity,
                delta_ionicity,
                sigma_an_cross,
                delta_sigma_an_cross,
                sigma_cat_cross,
                delta_sigma_cat_cross,
                t_self_an,
                delta_t_self_an,
                t_self_cat,
                delta_t_self_cat,
                t_an,
                delta_t_an,
                t_cat,
                delta_t_cat,
            ]
        ],
        columns=[
            "ionicity",
            "delta_ionicity",
            "sigma_an_cross",
            "delta_sigma_an_cross",
            "sigma_cat_cross",
            "delta_sigma_cat_cross",
            "t_self_an",
            "delta_t_self_an",
            "t_self_cat",
            "delta_t_self_cat",
            "t_an",
            "delta_t_an",
            "t_cat",
            "delta_t_cat",
        ],
    )

    print_results_to_stdout(results, a_posteriori)

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
    print_results_to_file(results, a_posteriori, args.output)

    return 0
