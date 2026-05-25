"""
Print functions for msdiff, conductivity
"""

from pathlib import Path

import pandas as pd


def print_program_header() -> None:
    """Print program header to stdout"""

    print("\n  \033[1mMSDiff Conductivity\033[0m")
    print("  ===================\n")


def print_results_to_stdout(
    results: pd.DataFrame,
    transport: pd.DataFrame,
) -> None:
    """Print results to stdout

    Parameters
    ----------
    results : pd.DataFrame
        Conductivity contributions to print
    transport : pd.DataFrame
        Transport numbers to print
    """

    print(f"\033[1mConductivity\033[0m")
    print(f"{'Contribution':<15} {'Sigma / S*m^-1':>20} {'R^2 fit':>10}")
    for i in range(len(results)):
        print(
            f"{results['contribution'].iloc[i]:<15} {results['sigma'].iloc[i]:>9.6f} ± {results['delta_sigma'].iloc[i]:>8.6f} {results['r2'].iloc[i]:>10.6f}"
        )
    print(
        f"\nLinear regime identified between {results['t_start'].iloc[0]:.2f} ps and {results['t_end'].iloc[0]:.2f} ps, with {results['n_data'].iloc[0]} data points used for the fit.\n"
    )

    print(f"\033[1mTransport Numbers\033[0m")
    print(f"{'Species':<8} {'t_ideal':>15} {'t_real':>19}")
    for i in range(len(transport)):
        print(
            f"{transport['species'].iloc[i]:<8} {transport['t_ideal'].iloc[i]:>9.6f} ± {transport['t_ideal_err'].iloc[i]:>8.6f} {transport['t_real'].iloc[i]:>9.6f} ± {transport['t_real_err'].iloc[i]:>8.6f}"
        )


def print_results_to_file(
    results: pd.DataFrame,
    transport: pd.DataFrame,
    output_file: str,
) -> None:
    """Print results to csv file

    Parameters
    ----------
    results : pd.DataFrame
        Conductivity contributions to print
    transport : pd.DataFrame
        Transport numbers to print
    output_file : str
        Name of output file (without extension)
    """

    # define output file
    out = Path(f"{output_file}_out.csv")
    tp = Path(f"{output_file}_tp.csv")

    with open(out, "w", encoding="utf8") as f:
        f.write(
            f"{'contribution':>15},{'sigma / S*m^-1':>16},{'delta_sigma / S*m^-1':>21},{'r2':>10}\n"
        )
        for i in range(len(results)):
            f.write(
                f"{results['contribution'].iloc[i]:>15},{results['sigma'].iloc[i]:>16.6f},{results['delta_sigma'].iloc[i]:>21.6f},{results['r2'].iloc[i]:>10.6f}\n"
            )
    print(f"\nResults written to {out}.")

    # adjust string format of species column
    transport["species"] = transport["species"].map(lambda x: f"{x:>8}")
    transport.to_csv(
        tp,
        sep=",",
        index=False,
        float_format="%16.8f",
        header=[
            f"{'species':>8}",
            f"{'t_ideal':>16}",
            f"{'delta_t_ideal':>16}",
            f"{'t_real':>16}",
            f"{'delta_t_real':>16}",
        ],
    )
    print(f"Transport numbers written to {tp}.\n")
