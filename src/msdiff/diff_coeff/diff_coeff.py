"""
Main script for msdiff.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from ..functions import find_linear_region, get_diffusion_coefficient
from ..plotting import generate_simple_plot
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
    # read the file and drop derivative column
    data = pd.read_csv(
        args.file, sep=";", skiprows=1, names=["time", "msd", "derivative"]
    )
    data = data.drop(columns=["derivative"])

    # prepare Hummer correction
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

    # identify the linear region
    firststep = find_linear_region(data, args.tolerance)
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
        data,
        firststep,
        args.temperature,
        args.viscosity,
        args.length,
        args.delta_viscosity,
    )

    # summarize results to data frame
    result_list = []
    result_list.append(
        [
            diff_coeff,
            delta_diff_coeff,
            k_hum,
            delta_k_hum,
            rsquared,
            data["time"][firststep],
            npoints_fit,
            len(data),
        ]
    )
    results = pd.DataFrame(
        data=result_list,
        columns=[
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

    print_results_to_stdout(results)

    # rename columns for file output
    results = results.rename(
        columns={
            "diff_coeff": "D / 10^-12 m^2/s",
            "delta_diff_coeff": "D_stderr / 10^-12 m^2/s",
            "k_hum": "K / 10^-12 m^2/s",
            "delta_k_hum": "K_std / 10^-12 m^2/s",
            "rsquared": "R^2",
            "fit_start": "Fit start / ps",
            "npoints_fit": "Npoints_fit",
            "npoints_data": "Npoints_data",
        }
    )

    print_results_to_file(results, args.output)

    # generate a plot if requested
    if args.plot:
        generate_simple_plot(data, firststep)  # pragma: no cover

    return 0
