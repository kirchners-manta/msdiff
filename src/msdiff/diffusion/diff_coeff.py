"""
Main script for msdiff diffusion coefficient calculation.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from ..functions import (
    calc_Hummer_correction,
    calc_orthoboxy_viscosity,
    find_linear_region,
    linear_fit,
)
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
        travis_path = Path(args.file[0]).parent / "travis.log"
        if os.path.isfile(travis_path):
            with open(travis_path, encoding="utf8") as f:
                for line in f:
                    if "Found cell geometry data in trajectory file" in line:
                        # read box length from the over next line
                        next(f)
                        line = next(f)
                        args.length = [
                            float(line.split()[2]),
                            float(line.split()[6]),
                            float(line.split()[10]),
                        ]
        else:
            raise FileNotFoundError("travis.log not found.")
    else:
        if args.length is None:
            raise ValueError("Box length not given.")
        elif type(args.length) == float:
            args.length = [
                float(args.length),
                float(args.length),
                float(args.length),
            ]
        elif len(args.length) == 2:
            args.length = [
                float(args.length[0]),
                float(args.length[0]),
                float(args.length[1]),
            ]
        elif len(args.length) == 3:
            args.length = [
                float(args.length[0]),
                float(args.length[1]),
                float(args.length[2]),
            ]
        else:
            raise ValueError("Too many box lengths given.")
    # if all components of the box length are equal, set cubic to true
    if args.length[0] == args.length[1] == args.length[2]:
        args.cubic = True
    else:
        args.cubic = False
    # for orthoboxy, don't need to give the box length
    if args.orthoboxy is not None:
        if args.cubic:
            raise ValueError("Cubic box does not make sense for OrthoBoXY.")
        args.dimensions = 2
        print(
            f"OrthoBoXY: Assuming MSD in x and y directions, with dimensions {args.dimensions}"
        )

    # read data from file
    data = pd.read_csv(
        args.file, sep=";", skiprows=1, names=["time", "msd", "msd_std"]
    ).astype(float)

    # debug
    # print(data)

    if not args.avg:
        # if 'avg' option is false, the file contains the MSD for a single molecule and the derivative (not needed), is skipped.
        data["msd_std"] = 0.0

    # determine linear region
    firststep, laststep = find_linear_region(data[["time", "msd"]], args.tolerance)

    # debug
    # print(f"firststep: {firststep}, laststep: {laststep}")

    # perform linear regression in the linear region
    if firststep == -1 or laststep == -1:
        raise ValueError(
            "No linear region found in the data. Please check the input file and the tolerance."
        )
    else:
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

    # divide D and delta D by 2*dimensions
    diff = slope / (2 * args.dimensions)
    delta_diff = delta_slope / (2 * args.dimensions)

    # hummer correction
    if args.cubic:
        k_hum, delta_k_hum = calc_Hummer_correction(
            args.hummer[0],
            args.hummer[1],
            args.length[0],
            args.hummer[2],
        )
    else:
        k_hum = delta_k_hum = 0.0

    # OrthoBoXY viscosity
    if args.orthoboxy is not None:
        data_z = pd.read_csv(
            args.orthoboxy, sep=";", skiprows=1, names=["time", "msd", "msd_std"]
        ).astype(float)

        if not args.avg:
            # if 'avg' option is false, the file contains the MSD for a single molecule and the derivative (not needed), is skipped.
            data_z["msd_std"] = 0.0

        slope_z, delta_slope_z, _, _ = linear_fit(
            data_z,
            firststep,
            laststep,
        )
        diff_z = slope_z / 2  # dimension is 1, only z direction
        delta_diff_z = delta_slope_z / 2

        # debug
        print(diff, delta_diff, diff_z, delta_diff_z, args.hummer[0], args.length[2])

        eta, delta_eta = calc_orthoboxy_viscosity(
            diff, delta_diff, diff_z, delta_diff_z, args.hummer[0], args.length[2]
        )

    # create a dictionary with the results
    results = {
        "diffusion": {
            "diffusion_coefficient": diff,
            "delta_diffusion_coefficient": delta_diff,
            "k_hummer": k_hum,
            "delta_k_hummer": delta_k_hum,
            "r2": r2,
            "t_fit_start": float(data["time"].iloc[firststep]),
            "t_fit_end": float(data["time"].iloc[laststep]),
            "n_data": npoints_fit,
            "lx": args.length[0],
            "ly": args.length[1],
            "lz": args.length[2],
            "diffusion_coefficient_z": diff_z if args.orthoboxy is not None else None,
            "delta_diffusion_coefficient_z": (
                delta_diff_z if args.orthoboxy is not None else None
            ),
            "eta": eta if args.orthoboxy is not None else None,
            "delta_eta": delta_eta if args.orthoboxy is not None else None,
        }
    }

    print_results_to_stdout(results)

    print_results_to_file(results, args.output)

    return 0
