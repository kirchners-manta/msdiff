"""
Print functions for msdiff, diffusion coefficient
"""

from pathlib import Path

import pandas as pd


def print_program_header() -> None:
    """Print program header to stdout"""

    print("\n  \033[1mMSDiff Diffusion\033[0m")
    print("  ================\n")


def print_results_to_stdout(results: pd.DataFrame) -> None:
    """Print results to stdout

    Parameters
    ----------
    results : pd.DataFrame
        Results to print
    """

    for i in range(len(results)):
        print(f"\033[1mSpecies {i+1}\033[0m")
        print(
            f"Diffusion coefficient: \t\t D_0 = ({results['diffusion_coefficient'].iloc[i]:>15.6f} ± {results['delta_diffusion_coefficient'].iloc[i]:>15.6f}) * 10^-12 m^2/s"
        )
        if "diffusion_coefficient_z" in results.columns:
            print(
                f"Diffusion coefficient (z): \t D_z = ({results['diffusion_coefficient_z'].iloc[i]:>15.6f} ± {results['delta_diffusion_coefficient_z'].iloc[i]:>15.6f}) * 10^-12 m^2/s"
            )
        print(
            f"Hummer correction term: \t K   = ({results['k_hummer'].iloc[i]:>15.6f} ± {results['delta_k_hummer'].iloc[i]:>15.6f}) * 10^-12 m^2/s"
        )
        if "eta" in results.columns and results["eta"].notnull().any():
            print(
                f"Viscosity: \t\t\t η   = ({results['eta'].iloc[i]:>15.6f} ± {results['delta_eta'].iloc[i]:>15.6f}) * 10^-3  Pa s"
            )
        print()


def print_results_to_file(
    results: pd.DataFrame,
    output_file: str,
) -> None:
    """Print results to csv file

    Parameters
    ----------
    results : pd.DataFrame
        Results to print
    output_file : str
        Output file
    """

    # write output to .csv file
    out = Path(f"{output_file}_out.csv")

    with open(out, "w", encoding="utf8") as f:
        if "diffusion_coefficient_z" not in results.columns:
            f.write(
                f"{'Species':>8},{'D_0 / 10^-12 m^2/s':>19},{'delta_D':>15},{'K / 10^-12 m^2/s':>17},{'delta_K':>15},{'r2':>15},{'t_start / ps':>15},{'t_end / ps':>15},{'n_data':>10}\n"
            )
            for i in range(len(results)):
                f.write(
                    f"{i+1:>8},{results['diffusion_coefficient'].iloc[i]:>19.6f},{results['delta_diffusion_coefficient'].iloc[i]:>15.6f},{results['k_hummer'].iloc[i]:>17.6f},{results['delta_k_hummer'].iloc[i]:>15.6f},{results['r2'].iloc[i]:>15.6f},{results['t_fit_start'].iloc[i]:>15.6f},{results['t_fit_end'].iloc[i]:>15.6f},{results['n_data'].iloc[i]:>10d}\n"
                )
        else:
            f.write(
                f"{'Species':>8},{'D_0 / 10^-12 m^2/s':>19},{'delta_D':>15},{'K / 10^-12 m^2/s':>17},{'delta_K':>15},{'r2':>15},{'t_start / ps':>15},{'t_end / ps':>15},{'n_data':>10},{'D_z / 10^-12 m^2/s':>19},{'delta_D_z':>15},{'eta / 10^-3 Pa s':>17},{'delta_eta':>15}\n"
            )
            for i in range(len(results)):
                f.write(
                    f"{i+1:>8},{results['diffusion_coefficient'].iloc[i]:>19.6f},{results['delta_diffusion_coefficient'].iloc[i]:>15.6f},{results['k_hummer'].iloc[i]:>17.6f},{results['delta_k_hummer'].iloc[i]:>15.6f},{results['r2'].iloc[i]:>15.6f},{results['t_fit_start'].iloc[i]:>15.6f},{results['t_fit_end'].iloc[i]:>15.6f},{results['n_data'].iloc[i]:>10d},{results['diffusion_coefficient_z'].iloc[i]:>19.6f},{results['delta_diffusion_coefficient_z'].iloc[i]:>15.6f},{results['eta'].iloc[i]:>17.6f},{results['delta_eta'].iloc[i]:>15.6f}\n"
                )

    print(f"Results written to {out}.\n")
