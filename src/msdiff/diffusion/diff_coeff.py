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
from .output import print_program_header, print_results_to_file, print_results_to_stdout


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

    # print program header
    print_program_header()

    # if 'from travis' option is true, check for the box length in travis output file
    if args.from_travis:
        travis_path = Path(args.file).parent / "travis.log"
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
                        print(
                            f"Info: Box lengths read from travis.log: {args.length} pm.\n"
                        )
        else:
            raise FileNotFoundError("travis.log not found.")
    else:
        if args.length is None:
            args.length = [0.0, 0.0, 0.0]
            print(
                "Info: No box length given, set to zero. Hummer correction will be zero.\n"
            )
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
            raise ValueError(
                "Cubic box does not make sense for OrthoBoXY mode. Please provide different box lengths for x and z direction.\n"
            )
        args.dimensions = 2
        print(
            f"Info: OrthoBoXY mode assumes MSD in the input file to be in x and y directions and the additional file contains the MSD in the z direction.\n"
        )

    # read data from file
    msd_data = read_input_diffusion(args.file, args.uncertainty, args.species)

    # read OrthoBoXY data if given
    if args.orthoboxy is not None:
        msd_data_z = read_input_diffusion(
            args.orthoboxy, args.uncertainty, args.species
        )

    # debug
    # print(msd_data)

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

    # initialize dataframe for results
    results_columns = [
        "diffusion_coefficient",
        "delta_diffusion_coefficient",
        "k_hummer",
        "delta_k_hummer",
        "r2",
        "t_fit_start",
        "t_fit_end",
        "n_data",
        "lx",
        "ly",
        "lz",
    ]
    if args.orthoboxy is not None:
        results_columns += [
            "diffusion_coefficient_z",
            "delta_diffusion_coefficient_z",
            "eta",
            "delta_eta",
        ]
    results = pd.DataFrame(columns=results_columns)

    # debug
    # print(results)

    # determine linear region
    for i in range(args.species):

        firststep, laststep = find_linear_region(
            msd_data[["time", f"msd_{i+1}_self"]],
            args.tolerance,
        )

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
                msd_data[["time", f"msd_{i+1}_self", f"msd_{i+1}_self_std"]],
                firststep,
                laststep,
            )

        # divide D and delta D by 2*dimensions
        diff = slope / (2 * args.dimensions)
        delta_diff = delta_slope / (2 * args.dimensions)

        # compute orthoboxy viscosity
        if args.orthoboxy is not None:

            # determine diffusion along z first
            slope_z, delta_slope_z, _, _ = linear_fit(
                msd_data_z[["time", f"msd_{i+1}_self", f"msd_{i+1}_self_std"]],
                firststep,
                laststep,
            )
            diff_z = slope_z / 2  # dimension is 1, only z direction
            delta_diff_z = delta_slope_z / 2

            # debug
            # print(diff, delta_diff, diff_z, delta_diff_z, args.hummer[0], args.length[2])

            # viscosity
            eta, delta_eta = calc_orthoboxy_viscosity(
                diff, delta_diff, diff_z, delta_diff_z, args.hummer[0], args.length[2]
            )

            # debug
            # print(f"{eta:.10f} ± {delta_eta:.10f} mPa·s")

        # add results to dataframe
        results.loc[i] = {
            "diffusion_coefficient": diff,
            "delta_diffusion_coefficient": delta_diff,
            "k_hummer": k_hum,
            "delta_k_hummer": delta_k_hum,
            "r2": r2,
            "t_fit_start": float(msd_data["time"].iloc[firststep]),
            "t_fit_end": float(msd_data["time"].iloc[laststep]),
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

        # debug
        # print(results)

    # print results
    print_results_to_stdout(results)
    print_results_to_file(results, args.output)

    return 0


def read_input_diffusion(file: str, uncert: str, species: int) -> pd.DataFrame:
    """Reads the input file for diffusion coefficient calculation.

    Parameters
    ----------
    file : str
        The path to the input file.
    uncert : str
        Type of uncertainty in the input file, either "std", "var" or "none".
    species : int
        The number of species in the system.

    Returns
    -------
    pd.DataFrame
        The input data as a pandas DataFrame.
    """

    if uncert == "none":
        # number of columns is 1 (time) + nspec (msd)
        ncols = 1 + species
        colnames = ["time"] + [f"msd_{i+1}_self" for i in range(species)]

        # read to pandas dataframe, do not assign column names yet
        data = pd.read_csv(
            file,
            sep=";",
            skiprows=1,
        ).astype(float)

        # get number of columns in the file
        # drop columns that are not needed and assign column names
        ncols_file = data.shape[1]
        if ncols_file != ncols:
            data = data.iloc[:, :ncols]
        data.columns = colnames

        # add columns for msd_std with value 0.0
        for i in range(species):
            data[f"msd_{i+1}_self_std"] = 0.0
    else:
        # number of columns is 1 (time) + nspec (msd) + nspec (uncertainty)
        ncols = 1 + 2 * species
        colnames = ["time"] + [
            f"msd_{i+1}_{j}" for i in range(species) for j in ["self", "self_std"]
        ]
        # read to pandas dataframe
        data = pd.read_csv(
            file,
            sep=";",
            skiprows=1,
        ).astype(float)

        # debug
        # print(data)
        # print(colnames)

        # get number of columns in the file
        # drop columns that are not needed and assign column names
        ncols_file = data.shape[1]
        if ncols_file != ncols:
            data = data.iloc[:, :ncols]
        data.columns = colnames

        if uncert == "var":
            # convert variance to standard deviation
            for i in range(species):
                data[f"msd_{i+1}_self_std"] = data[f"msd_{i+1}_self_std"].apply(
                    lambda x: x**0.5
                )

    return data
