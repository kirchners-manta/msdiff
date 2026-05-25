"""
Main file for the ionic conductivity calculation.
"""

from __future__ import annotations

import argparse

import pandas as pd

from ..functions import calc_transport_numbers, find_linear_region, linear_fit
from .output import print_program_header, print_results_to_file, print_results_to_stdout


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

    # print program header
    print_program_header()

    # read data from file
    msd_data = read_input_conductivity(args.file, args.uncertainty, args.species)

    # find linear region, based on EH conductivity
    (firststep, laststep) = find_linear_region(
        msd_data[["time", "total_eh"]],
        args.tolerance,
    )

    # initialize dataframe for results
    results = pd.DataFrame(
        columns=[
            "contribution",
            "sigma",
            "delta_sigma",
            "r2",
            "t_start",
            "t_end",
            "n_data",
        ],
    )

    # loop over all contributions
    contributions = (
        [f"msd_{i+1}_self" for i in range(args.species)]
        + [f"msd_{i+1}_cross" for i in range(args.species)]
        + [
            f"msd_{i+1}_{j+1}"
            for i in range(args.species)
            for j in range(i + 1, args.species)
        ]
        + ["total_eh"]
    )
    for c, data_set in enumerate(contributions):

        # perform linear fit
        if firststep == -1 or laststep == -1:
            raise ValueError(
                "No linear region found in the data. Please check the input file and the tolerance."
            )
        else:
            cond, delta_cond, r2, npoints_fit = linear_fit(
                msd_data[["time", data_set, f"{data_set}_std"]],
                firststep,
                laststep,
            )

        # add results to dataframe
        results.loc[c] = {
            "contribution": data_set,
            "sigma": cond,
            "delta_sigma": delta_cond,
            "r2": r2,
            "t_start": float(msd_data["time"].iloc[firststep]),
            "t_end": float(msd_data["time"].iloc[laststep]),
            "n_data": npoints_fit,
        }

    # debug
    # print(results)

    # calculate transport numbers
    transport_numbers = calc_transport_numbers(results, args.species)

    print_results_to_stdout(results, transport_numbers)
    print_results_to_file(results, transport_numbers, args.output)

    return 0


def read_input_conductivity(file: str, uncert: str, species: int) -> pd.DataFrame:
    """Read input data from file

    Parameters
    ----------
    file : str
        Input file
    uncert : str
        Type of uncertainty in the input file, either "std", "var" or "none"
    species : int
        Number of species in the system

    Returns
    -------
    pd.DataFrame
        Dataframe containing the input data
    """

    if uncert == "none":
        # number of columns is 1 (time) + 1 (total conductivity) + 2 * nspec (self and cross conductivity) + nspec * (nspec - 1) / 2 (two-body contributions)
        ncols = 1 + 1 + 2 * species + (species * (species - 1)) // 2
        colnames = (
            ["time"]
            + [f"msd_{i+1}_self" for i in range(species)]
            + [f"msd_{i+1}_cross" for i in range(species)]
            + [
                f"msd_{i+1}_{j+1}"
                for i in range(species)
                for j in range(i + 1, species)
            ]
            + ["total_eh"]
        )

        data = pd.read_csv(
            file,
            sep=";",
            skiprows=1,
        ).astype(float)

        # if there are more columns in the file than expected, drop them
        ncols_file = data.shape[1]
        if ncols_file > ncols:
            data = data.iloc[:, :ncols]
        data.columns = colnames

        # add columns for standard error and set them to zero
        for i in range(species):
            data[f"msd_{i+1}_self_std"] = 0.0
            data[f"msd_{i+1}_cross_std"] = 0.0
            for j in range(i + 1, species):
                data[f"msd_{i+1}_{j+1}_std"] = 0.0
        data["total_eh_std"] = 0.0
    else:
        # number of columns is 1 (time) + [1 (total conductivity) + 2 * nspec (self and cross conductivity) + nspec * (nspec - 1) / 2 (two-body contributions)] * 2 data and uncertainty)
        ncols = 1 + 2 + 4 * species + (species * (species - 1))
        colnames = (
            ["time"]
            + [f"msd_{i+1}_{j}" for i in range(species) for j in ["self", "self_std"]]
            + [f"msd_{i+1}_{j}" for i in range(species) for j in ["cross", "cross_std"]]
            + [
                f"msd_{i+1}_{j+1}{k}"
                for i in range(species)
                for j in range(i + 1, species)
                for k in ["", "_std"]
            ]
            + ["total_eh"]
            + [f"total_eh_std"]
        )

        # debug
        # print(colnames)

        data = pd.read_csv(
            file,
            sep=";",
            skiprows=1,
        ).astype(float)

        # if there are more columns in the file than expected, drop them
        ncols_file = data.shape[1]
        if ncols_file > ncols:
            data = data.iloc[:, :ncols]
        data.columns = colnames

        if uncert == "var":
            # convert variance to standard deviation
            for i in range(species):
                data[f"msd_{i+1}_self_std"] = data[f"msd_{i+1}_self_std"].apply(
                    lambda x: x**0.5
                )
                data[f"msd_{i+1}_cross_std"] = data[f"msd_{i+1}_cross_std"].apply(
                    lambda x: x**0.5
                )
                for j in range(i + 1, species):
                    data[f"msd_{i+1}_{j+1}_std"] = data[f"msd_{i+1}_{j+1}_std"].apply(
                        lambda x: x**0.5
                    )
            data["total_eh_std"] = data["total_eh_std"].apply(lambda x: x**0.5)

    # debug
    # print(data)

    return data
