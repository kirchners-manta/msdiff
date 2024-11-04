"""
Print functions for msdiff, conductivity
"""

from __future__ import annotations

import pandas as pd  # type: ignore
from pathlib import Path


def print_results_to_stdout(
    results: pd.DataFrame,
    a_posteriori: pd.DataFrame,
) -> None:
    print("  \033[1mMSDiff Conductivity\033[0m")
    print("  ===================")
    print(f"\nContributions to the conductivity")
    # print the results per row
    for i, row in results.iterrows():
        print(
            f"{row['contribution']:<23}:  {row['sigma']:7.4f} ± {row['delta_sigma']:7.4f} S/m"
        )
    print(f"\nA posteriori quantities")
    for i, col in enumerate(a_posteriori.columns):
        if i % 2 == 0:
            print(
                f"{col:<11}:  {a_posteriori.iloc[0, i]:7.4f} ± {a_posteriori.iloc[0, i+1]:7.4f}"
            )


def print_results_to_file(
    results: pd.DataFrame,
    a_porsteriori: pd.DataFrame,
    output_file: str,
) -> None:
    # define output file
    out = Path(f"{output_file}_out.csv")
    out_post = Path(f"{output_file}_post.csv")

    results.to_csv(
        out,
        sep=",",
        index=False,
        float_format="%16.8f",
        header=[
            "contribution",
            "sigma / S*m^-1",
            "delta_sigma / S*m^-1",
            "r2",
            "t_start / ps",
            "t_end / ps",
            "n_data_fit",
        ],
    )
    print(f"\nResults written to {out}")

    a_porsteriori.to_csv(
        out_post,
        sep=",",
        index=False,
        float_format="%16.8f",
    )
    print(f"A posteriori quantities written to {out_post}")
