"""
Main script for msdiff.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
import numpy as np

from ..functions import (
    find_linear_region,
    get_diffusion_coefficient,
)
from ..plotting import generate_simple_plot
from .output import print_results_to_file, print_results_to_stdout
from .input import process_input


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
        travis_path = Path(args.file).parent / "travis.log"  # type: ignore
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
    # initialize list for results
    result_list = []

    # read data from file
    data, nmols = process_input(args.file)

    for i in range(nmols):
        # select data for one molecule
        mol_data = data[["time", f"msd_{i+1}"]]

        # identify the linear region
        firststep = find_linear_region(mol_data, i, args.tolerance)
        if firststep == -1:
            raise ValueError("No linear region found.")

        # perform linear regression in the linear region
        (
            diff_coeff,
            delta_diff_coeff,
            rsquared,
            npoints_fit,
            k_hum,
            delta_k_hum,
        ) = get_diffusion_coefficient(
            mol_data,
            i,
            firststep,
            args.temperature,
            args.viscosity,
            args.length,
            args.delta_viscosity,
        )

        # if i > 0, the hummer correction is not calculated but copied from the first molecule
        if i > 0:
            k_hum = result_list[0][2]
            delta_k_hum = result_list[0][3]

        # summarize results to data frame
        result_list.append(
            [
                i + 1,
                diff_coeff,
                delta_diff_coeff,
                k_hum,
                delta_k_hum,
                rsquared,
                mol_data["time"][firststep],
                npoints_fit,
                len(mol_data),
            ]
        )
        results = pd.DataFrame(
            data=result_list,
            columns=[
                "Molecule",
                "diff_coeff",
                "delta_diff_coeff",
                "k_hum",
                "delta_k_hum",
                "rsquared",
                "fit_start",
                "npoints_fit",
                "npoints_data",
            ],
        )

    # calculate average results
    if nmols > 1:
        avg_diff_coeff = results["diff_coeff"].mean()
        delta_avg_diff_coeff = results["diff_coeff"].std() / np.sqrt(nmols)
    elif nmols == 1:
        avg_diff_coeff = results["diff_coeff"][0]
        delta_avg_diff_coeff = results["delta_diff_coeff"][0]

    print_results_to_stdout(results, nmols, avg_diff_coeff, delta_avg_diff_coeff)

    # rename columns for file output
    results = results.rename(
        columns={
            "diff_coeff": "D / 10^-12 m^2/s",
            "delta_diff_coeff": "D_stderr / 10^-12 m^2/s",
            "k_hum": "K / 10^-12 m^2/s",
            "delta_k_hum": "K_stddev / 10^-12 m^2/s",
            "rsquared": "R^2",
            "fit_start": "Fit start / ps",
            "npoints_fit": "Npoints_fit",
            "npoints_data": "Npoints_data",
        }
    )
    results_avg = pd.DataFrame(
        data=[
            [
                avg_diff_coeff,
                delta_avg_diff_coeff,
                results["K / 10^-12 m^2/s"][0],
                results["K_stddev / 10^-12 m^2/s"][0],
            ]
        ],
        columns=[
            "D_avg / 10^-12 m^2/s",
            "D_avg_stderr / 10^-12 m^2/s",
            "K / 10^-12 m^2/s",
            "K_stddev / 10^-12 m^2/s",
        ],
    )

    print_results_to_file(results, results_avg, args.output)

    # generate a plot if requested
    # if args.plot:
    #     generate_simple_plot(data, firststep)  # pragma: no cover

    return 0
