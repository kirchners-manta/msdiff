"""
Main script for msdiff diffusion coefficient calculation.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List, Union

import numpy as np
import pandas as pd  # type: ignore

from ..functions import calc_Hummer_correction, find_linear_region, linear_fit
from .output import print_results_to_file, print_results_to_stdout


def diffusion_coefficient(args: argparse.Namespace) -> int:
    """Main function of the MSDiff program.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed command line arguments.

    Returns
    -------
    int
        The exit code of the program.

    Raises
    ------
    ValueError
        If no linear region is found in the data.
    """

    # if 'from travis' option is true, check for the box length in travis output file
    if args.from_travis:
        travis_path = Path(args.file).parent / "travis.log"
        if os.path.isfile(travis_path):
            with open(travis_path, "r", encoding="utf8") as f:
                for line in f:
                    if "Found cell geometry data in trajectory file" in line:
                        # read box length from the over next line
                        next(f)
                        line = next(f)
                        args.length = float(line.split()[2])
        else:
            raise FileNotFoundError("travis.log not found.")

    # if length is not given, raise error
    if args.length is None:
        raise ValueError("Box length not given.")

    # read data from file
    if args.avg:
        # if 'avg' option is true, the file contains the average values and the standard deviation
        data = pd.read_csv(
            args.file, sep=";", skiprows=1, names=["time", "msd", "msd_std"]
        ).astype(float)
    else:
        # if 'avg' option is false, the file contains the MSD for a single molecule and the derivative (not needed), the default output of TRAVIS
        data = pd.read_csv(
            args.file, sep=";", skiprows=1, names=["time", "msd", "derivative"]
        ).astype(float)
        # drop the derivative column and add std column as zeros
        data = data.drop(columns=["derivative"])
        data["msd_std"] = 0.0

    # determine linear region
    (firststep, laststep) = find_linear_region(data[["time", "msd"]], args.tolerance)

    # perform linear regression in the linear region
    (
        slope,
        delta_slope,
        r2,
        npoints_fit,
    ) = linear_fit(
        data,
        firststep,
        laststep,
    )
    # debug
    # print(data)
    # print(f"firststep: {firststep}")
    # print(f"laststep: {laststep}")
    # print(f"diff: {slope}")
    # print(f"delta_diff: {delta_slope}")
    # print(f"r2: {r2}")
    # print(f"npoints_fit: {npoints_fit}")

    # divide D and delta D by 2*dimensions
    diff = slope / (2 * args.dimensions)
    delta_diff = delta_slope / (2 * args.dimensions)

    # hummer correction
    (k_hum, delta_k_hum) = calc_Hummer_correction(
        args.temperature,
        args.viscosity,
        args.length,
        args.delta_viscosity,
    )

    results_list = []

    # summarize results to data frame
    results_list.append(
        [
            diff,
            delta_diff,
            k_hum,
            delta_k_hum,
            r2,
            firststep,
            laststep,
            npoints_fit,
        ]
    )
    results = pd.DataFrame(
        data=results_list,
        columns=[
            "diff",
            "delta_diff",
            "k_hum",
            "delta_k_hum",
            "r2",
            "t_start",
            "t_end",
            "n_data",
        ],
    ).astype(
        {
            "diff": float,
            "delta_diff": float,
            "k_hum": float,
            "delta_k_hum": float,
            "r2": float,
            "t_start": float,
            "t_end": float,
            "n_data": int,
        }
    )

    print_results_to_stdout(results)

    print_results_to_file(results, args.output)

    return 0
