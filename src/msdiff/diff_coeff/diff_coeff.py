"""
Main script for msdiff.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from ..functions import (
    find_linear_region,
    get_diffusion_coefficient,
)
from ..plotting import generate_simple_plot


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
        r2,
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

    # print results
    print("  \033[1mMSDiff results\033[0m")
    print(
        f"Diffusion coefficient: \t\t D = ({diff_coeff:.8f} ± {delta_diff_coeff:.8f}) * 10^-12 m^2/s"
    )
    print(
        f"Hummer correction term: \t K = ({k_hum:.8f} ± {delta_k_hum:.8f}) * 10^-12 m^2/s"
    )
    print(f"Fit quality: \t\t\t R^2 = {r2:.8f}")
    print(f"Linear region started at \t t = {data['time'][firststep]:.8f}")
    print(f"Used {npoints_fit} of {len(data)} points for fit.")
    results = []
    results.append(
        [
            f"{diff_coeff:.8f}",
            f"{delta_diff_coeff:.8f}",
            f"{k_hum:.8f}",
            f"{r2:.8f}",
            f"{data['time'][firststep]:.8f}",
            npoints_fit,
            len(data),
        ]
    )

    # write results to csv file
    output = pd.DataFrame(
        data=results,
        columns=[
            "D / 10^-12 m^2/s",
            "D_std / 10^-12 m^2/s",
            "K_hummer / 10^-12 m^2/s",
            "R^2",
            "Lin reg start at t =",
            "Npoints_fit",
            "Npoints_total",
        ],
    )
    output.to_csv(args.output, index=False)

    # generate a plot if requested
    if args.plot:
        generate_simple_plot(data, firststep)  # pragma: no cover

    return 0
