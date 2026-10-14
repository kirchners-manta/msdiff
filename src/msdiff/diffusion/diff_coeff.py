"""
Main script for msdiff diffusion coefficient calculation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..functions import (
    calc_Hummer_correction,
    calc_orthoboxy_viscosity,
    find_linear_region,
    linear_fit,
)
from .output import print_program_header, print_results_to_file, print_results_to_stdout


def read_box_length_from_travis(travis_path: Path) -> list[float]:
    """Read the box lengths from a TRAVIS log file.

    Parameters
    ----------
    travis_path : Path
        Path to the ``travis.log`` file.

    Returns
    -------
    list[float]
        Box lengths ``[lx, ly, lz]`` in pm.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the log file contains no cell geometry.
    """
    if not travis_path.is_file():
        raise FileNotFoundError("travis.log not found.")

    length: list[float] | None = None
    with open(travis_path, encoding="utf8") as f:
        for line in f:
            if "Found cell geometry data in trajectory file" in line:
                # read box length from the over next line
                next(f)
                line = next(f)
                length = [
                    float(line.split()[2]),
                    float(line.split()[6]),
                    float(line.split()[10]),
                ]
    if length is None:
        raise ValueError("No cell geometry found in travis.log.")
    return length


def resolve_box_length(
    length: float | list[float] | None,
    from_travis: bool,
    input_file: str | Path,
) -> list[float]:
    """Determine the three box lengths from the command line input.

    Parameters
    ----------
    length : float | list[float] | None
        Value of ``--length``: a single value (cubic box), two values
        (``lx`` and ``lz``, with ``ly = lx``), three values, or ``None``.
    from_travis : bool
        Whether the box lengths are read from the ``travis.log`` next to the
        input file (``--from-travis``); ``length`` is ignored in that case.
    input_file : str | Path
        Path to the MSD input file.

    Returns
    -------
    list[float]
        Box lengths ``[lx, ly, lz]`` in pm; all zero if no length is given.

    Raises
    ------
    FileNotFoundError
        If ``from_travis`` is set but no ``travis.log`` exists.
    ValueError
        If more than three lengths are given or ``travis.log`` contains no
        cell geometry.
    """
    if from_travis:
        travis_length = read_box_length_from_travis(
            Path(input_file).parent / "travis.log"
        )
        print(f"Info: Box lengths read from travis.log: {travis_length} pm.\n")
        return travis_length

    if length is None:
        print(
            "Info: No box length given, set to zero. Hummer correction will be zero.\n"
        )
        return [0.0, 0.0, 0.0]
    if isinstance(length, float):
        return [length, length, length]
    if len(length) == 2:
        return [float(length[0]), float(length[0]), float(length[1])]
    if len(length) == 3:
        return [float(length[0]), float(length[1]), float(length[2])]
    raise ValueError("Too many box lengths given.")


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
    FileNotFoundError
        If ``--from-travis`` is set but no ``travis.log`` exists next to the
        input file.
    ValueError
        If the box lengths cannot be determined or are inconsistent (more than
        three values, cubic box in OrthoBoXY mode, no cell geometry in
        ``travis.log``), or if no linear region is found in the data.
    """

    # print program header
    print_program_header()

    # ``args`` is treated as read-only: everything derived from it lives in locals
    length = resolve_box_length(args.length, args.from_travis, args.file)
    # if all components of the box length are equal, the box is cubic
    cubic = length[0] == length[1] == length[2]
    dimensions: int = args.dimensions
    # for orthoboxy, don't need to give the box length
    if args.orthoboxy is not None:
        if cubic:
            raise ValueError(
                "Cubic box does not make sense for OrthoBoXY mode. Please provide different box lengths for x and z direction.\n"
            )
        dimensions = 2
        print(
            "Info: OrthoBoXY mode assumes MSD in the input file to be in x and y directions and the additional file contains the MSD in the z direction.\n"
        )

    # read data from file
    msd_data = read_input_diffusion(args.file, args.uncertainty, args.species)

    # read OrthoBoXY data if given
    if args.orthoboxy is not None:
        msd_data_z = read_input_diffusion(
            args.orthoboxy, args.uncertainty, args.species
        )

    # hummer correction
    if cubic:
        k_hum, delta_k_hum = calc_Hummer_correction(
            args.hummer[0],
            args.hummer[1],
            length[0],
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

    # determine linear region
    for i in range(args.species):

        firststep, laststep = find_linear_region(
            msd_data[["time", f"msd_{i+1}_self"]],
            args.tolerance,
            args.linreg_slice,
            args.linreg_incr,
        )

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
        diff = slope / (2 * dimensions)
        delta_diff = delta_slope / (2 * dimensions)

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

            # viscosity
            eta, delta_eta = calc_orthoboxy_viscosity(
                diff, delta_diff, diff_z, delta_diff_z, args.hummer[0], length[2]
            )

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
            "lx": length[0],
            "ly": length[1],
            "lz": length[2],
            "diffusion_coefficient_z": diff_z if args.orthoboxy is not None else None,
            "delta_diffusion_coefficient_z": (
                delta_diff_z if args.orthoboxy is not None else None
            ),
            "eta": eta if args.orthoboxy is not None else None,
            "delta_eta": delta_eta if args.orthoboxy is not None else None,
        }

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

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    ValueError
        If the file contains non-numeric data.
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
            # the line after the comment is data, not a header (the column
            # names are assigned below)
            header=None,
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
            # the line after the comment is data, not a header (the column
            # names are assigned below)
            header=None,
        ).astype(float)

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
