"""
Print functions for msdiff, diffusion coefficient
"""

from __future__ import annotations

from pathlib import Path


def print_results_to_stdout(results: dict[str, dict[str, float | int | None]]) -> None:
    """Print results to stdout

    Parameters
    ----------
    results : dict
        Results to print
    """

    print("  \033[1mMSDiff Diffusion\033[0m")
    print("  ================")

    print(
        f"Diffusion coefficient: \t\t D_0 = ({results['diffusion']['diffusion_coefficient']:>15.6f} ± {results['diffusion']['delta_diffusion_coefficient']:>15.6f}) * 10^-12 m^2/s"
    )
    if results["diffusion"]["diffusion_coefficient_z"] is not None:
        print(
            f"Diffusion coefficient (z): \t D_z = ({results['diffusion']['diffusion_coefficient_z']:>15.6f} ± {results['diffusion']['delta_diffusion_coefficient_z']:>15.6f}) * 10^-12 m^2/s"
        )
    print(
        f"Hummer correction term: \t K   = ({results['diffusion']['k_hummer']:>15.6f} ± {results['diffusion']['delta_k_hummer']:>15.6f}) * 10^-12 m^2/s"
    )
    if results["diffusion"]["eta"] is not None:
        print(
            f"Viscosity: \t\t\t η   = ({results['diffusion']['eta']:>15.6f} ± {results['diffusion']['delta_eta']:>15.6f}) * 10^-3  Pa s"
        )


def print_results_to_file(
    results: dict[str, dict[str, float | int | None]],
    output_file: str,
) -> None:
    """Print results to csv file

    Parameters
    ----------
    results : dict
        Results to print
    output_file : str
        Output file
    """

    # write output to .csv file
    out = Path(f"{output_file}_out.csv")

    with open(out, "w", encoding="utf8") as f:
        if (
            results["diffusion"]["diffusion_coefficient_z"] is None
            and results["diffusion"]["eta"] is None
        ):
            f.write(
                f"{'D_0 / 10^-12 m^2/s':>19},{'delta_D':>15},{'K / 10^-12 m^2/s':>17},{'delta_K':>15},{'r2':>15},{'t_start / ps':>15},{'t_end / ps':>15},{'n_data':>10}\n"
            )
            f.write(
                f"{results['diffusion']['diffusion_coefficient']:>19.6f},{results['diffusion']['delta_diffusion_coefficient']:>15.6f},{results['diffusion']['k_hummer']:>17.6f},{results['diffusion']['delta_k_hummer']:>15.6f},{results['diffusion']['r2']:>15.6f},{results['diffusion']['t_fit_start']:>15.6f},{results['diffusion']['t_fit_end']:>15.6f},{results['diffusion']['n_data']:>10d}\n"
            )
        else:
            f.write(
                f"{'D_0 / 10^-12 m^2/s':>19},{'delta_D':>15},{'K / 10^-12 m^2/s':>17},{'delta_K':>15},{'r2':>15},{'t_start / ps':>15},{'t_end / ps':>15},{'n_data':>10},{'D_z / 10^-12 m^2/s':>19},{'delta_D_z':>15},{'eta / 10^-3 Pa s':>17},{'delta_eta':>15}\n"
            )
            f.write(
                f"{results['diffusion']['diffusion_coefficient']:>19.6f},{results['diffusion']['delta_diffusion_coefficient']:>15.6f},{results['diffusion']['k_hummer']:>17.6f},{results['diffusion']['delta_k_hummer']:>15.6f},{results['diffusion']['r2']:>15.6f},{results['diffusion']['t_fit_start']:>15.6f},{results['diffusion']['t_fit_end']:>15.6f},{results['diffusion']['n_data']:>10d},{results['diffusion']['diffusion_coefficient_z']:>19.6f},{results['diffusion']['delta_diffusion_coefficient_z']:>15.6f},{results['diffusion']['eta']:>17.6f},{results['diffusion']['delta_eta']:>15.6f}\n"
            )

    print(f"Results written to {out}")
