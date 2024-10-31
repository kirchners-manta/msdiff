"""
Input reader for MSDiff diffusion
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd  # type: ignore


def process_input(input_file: str | Path) -> tuple[pd.DataFrame, int]:
    """Processes the input file

    Parameters
    ----------
    input_file : str | Path
        Path to the input file

    Returns
    -------
    tuple[pd.DataFrame, int]
        The data and the number of molecules

    Raises
    ------
    ValueError
        If the input file has the wrong number of columns
    """
    nmols = 0
    with open(input_file, "r", encoding="utf8") as f:
        ncols = len(f.readline().split(";"))

    if ncols == 2:  # standard input from other programs
        data = pd.read_csv(input_file, sep=";", skiprows=1, names=["time", "msd_1"])
        nmols = 1

    elif ncols == 3:  # standard input from TRAVIS
        data = pd.read_csv(
            input_file, sep=";", skiprows=1, names=["time", "msd_1", "derivative"]
        )
        data = data.drop(columns=["derivative"])
        nmols = 1

    elif ncols > 3:  # non-standard input from TRAVIS, e.g. MSD per molecule
        data = pd.read_csv(
            input_file,
            sep=";",
            skiprows=1,
            names=["time", "msd_total"] + [f"msd_{i+1}" for i in range(ncols - 2)],
        )
        nmols = ncols - 2
    else:
        raise ValueError("Input file has wrong number of columns.")

    return data, nmols
