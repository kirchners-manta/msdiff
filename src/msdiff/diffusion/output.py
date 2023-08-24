"""
Print functions for msdiff, diffusion coefficient
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path


def print_results_to_stdout(
    results: pd.DataFrame,
    nmols: int,
    avg_diff_coeff: float,
    delta_avg_diff_coeff: float,
) -> None:
    """Print results to stdout

    Parameters
    ----------
    results : pd.DataFrame
        Results to print
    nmols : int
        Number of molecules / data sets evaluated
    avg_diff_coeff : float
        Average diffusion coefficient in 10^-12 m^2/s
    delta_avg_diff_coeff : float
        Standard error of the average diffusion coefficient in 10^-12 m^2/s
    """

    print("  \033[1mMSDiff Diffusion\033[0m")
    print("  ===================")
    print(f"Analyzed {nmols} data sets:")

    print(
        f"Diffusion coefficient: \t\t D = ({avg_diff_coeff:.8f} ± {delta_avg_diff_coeff:.8f}) * 10^-12 m^2/s"
    )
    print(
        f"Hummer correction term: \t K = ({results['k_hum'][0]:.8f} ± {results['delta_k_hum'][0]:.8f}) * 10^-12 m^2/s"
    )


def print_results_to_file(
    results: pd.DataFrame,
    results_avg: pd.DataFrame,
    output_file: str | Path,
) -> None:
    """Print results to csv file

    Parameters
    ----------
    results : pd.DataFrame
        Results to print
    results_avg : pd.DataFrame
        Average results to print
    output_file : str | Path
        Output file
    """
    # write msdiff_mols.csv to same directory as output_file
    output_mols = Path(output_file).parent / "msdiff_mols.csv"

    results.to_csv(output_mols, sep=",", index=False)
    print(f"\nIndividual results written to msdiff_mols.csv")
    results_avg.to_csv(output_file, sep=",", index=False)
    print(f"Average results written to {output_file}")
