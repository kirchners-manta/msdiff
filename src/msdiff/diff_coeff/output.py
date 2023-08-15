"""
Print functions for msdiff
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path


def print_results_to_stdout(results: pd.DataFrame) -> None:
    """Print results to stdout

    Parameters
    ----------
    results : pd.DataFrame
        Results to print
    """

    print("  \033[1mMSDiff results\033[0m")

    print(
        f"Diffusion coefficient: \t\t D = ({results['diff_coeff'][0]:.8f} ± {results['delta_diff_coeff'][0]:.8f}) * 10^-12 m^2/s"
    )
    print(
        f"Hummer correction term: \t K = ({results['k_hum'][0]:.8f} ± {results['delta_k_hum'][0]:.8f}) * 10^-12 m^2/s"
    )
    print(f"Fit quality: \t\t\t R^2 = {results['rsquared'][0]:.8f}")
    print(f"Linear region started at \t t = {results['fit_start'][0]:.8f}")
    print(
        f"Used {results['npoints_fit'][0]} of {results['npoints_data'][0]} points for fit."
    )


def print_results_to_file(results: pd.DataFrame, output_file: str | Path) -> None:
    """Print results to csv file

    Parameters
    ----------
    results : pd.DataFrame
        Results to print
    output_file : str | Path
        Output file
    """
    results.to_csv(output_file, sep=",", index=False)
