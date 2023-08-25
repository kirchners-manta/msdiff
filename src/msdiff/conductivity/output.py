"""
Print functions for msdiff, conductivity
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path


def print_results_to_stdout(
    results: pd.DataFrame,
    a_posteriori: pd.DataFrame,
) -> None:
    print("  \033[1mMSDiff Conductivity\033[0m")
    print("  ===================")
    print(f"\nContributions")
    # print the results per row
    for i, row in results.iterrows():
        print(
            f"{row['Contribution']:<15}:  {row['sigma']:.4f} +- {row['delta_sigma']:.4f} S/m"
        )
        # for debugging
        # print(
        #     f"{row['Contribution']:<15}:  {row['sigma']:.4f} +- {row['delta_sigma']:.4f} S/m, {row['t_start']:.2f} - {row['t_end']:.2f} ps, {row['n_data']} data points"
        # )
    print(f"\nA posteriori quantities")
    for i, col in enumerate(a_posteriori.columns):
        if i % 2 == 0:
            if col == "sigma_an_cross" or col == "sigma_cat_cross":
                print(
                    f"{col:<15}:  {a_posteriori.iloc[0, i]:.4f} +- {a_posteriori.iloc[0, i+1]:.4f} S/m"
                )
            else:
                print(
                    f"{col:<15}:  {a_posteriori.iloc[0, i]:.4f} +- {a_posteriori.iloc[0, i+1]:.4f}"
                )


def print_results_to_file(
    results: pd.DataFrame,
    a_porsteriori: pd.DataFrame,
    output_file: str | Path,
) -> None:
    # write other results to same directory as output_file
    out_posteriori = Path(output_file).parent / "msdiff_post.csv"

    results.to_csv(output_file, sep=",", index=False)
    print(f"\nResults written to {output_file}")
    a_porsteriori.to_csv(out_posteriori, sep=",", index=False)
    print(f"A posteriori quantities written to {out_posteriori}")
