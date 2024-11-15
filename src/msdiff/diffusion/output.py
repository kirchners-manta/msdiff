"""
Print functions for msdiff, diffusion coefficient
"""

from __future__ import annotations

import pandas as pd  # type: ignore
from pathlib import Path


def print_results_to_stdout(
    results: pd.DataFrame,
) -> None:
    """Print results to stdout

    Parameters
    ----------
    results : pd.DataFrame
        Results to print
    """

    print("  \033[1mMSDiff Diffusion\033[0m")
    print("  ================")

    print(
        f"Diffusion coefficient: \t\t D = ({results['diff'][0]:12.8f} ± {results['delta_diff'][0]:12.8f}) * 10^-12 m^2/s"
    )
    print(
        f"Hummer correction term: \t K = ({results['k_hum'][0]:12.8f} ± {results['delta_k_hum'][0]:12.8f}) * 10^-12 m^2/s"
    )


def print_results_to_file(
    results: pd.DataFrame,
    output_file: str,
) -> None:
    """Print results to csv file

    Parameters
    ----------
    results : pd.DataFrame
        Results to print
    results_avg : pd.DataFrame
        Average results to print
    output_file : str
        Output file
    """
    # write msdiff_mols.csv to same directory as output_file
    out = Path(f"{output_file}_out.csv")

    results.to_csv(
        out,
        sep=",",
        index=False,
        header=[
            "D / 10^-12 m^2/s",
            "delta_D / 10^-12 m^2/s",
            "K / 10^-12 m^2/s",
            "delta_K / 10^-12 m^2/s",
            "r2",
            "t_start / ps",
            "t_end / ps",
            "n_data_fit",
        ],
        float_format="%16.8f",
    )
    print(f"Results written to {out}")
