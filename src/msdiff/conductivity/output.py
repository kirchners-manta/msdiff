"""
Print functions for msdiff, conductivity
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path


def print_results_to_stdout(
    results: pd.DataFrame,
) -> None:
    print("  \033[1mMSDiff Conductivity\033[0m")
    print("  ===================")
    print(f"\nContributions")
    # print the results per row
    for i, row in results.iterrows():
        print(
            f"{row['Contribution']:<13}:  {row['sigma']:.4f} +- {row['delta_sigma']:.4f} S/m"
        )


def print_results_to_file(
    results: pd.DataFrame,
    output_file: str | Path,
) -> None:
    # write msdiff_mols.csv to same directory as output_file
    results.to_csv(output_file, sep=",", index=False)
    print(f"\nResults written to {output_file}")
