"""
Main script for msdiff.
"""

from __future__ import annotations

import argparse

import pandas as pd

from ..functions import (calc_Hummer_correction, find_linear_region,
                         perform_linear_regression)
from ..plotting import generate_simple_plot


def diffusion_coefficient(args: argparse.Namespace) -> int:

    # read the file and drop derivative column
    data = pd.read_csv(args.file, sep=";", skiprows=1, names=["time", "msd", "derivative"])
    data = data.drop(columns=["derivative"])

    # identify the linear region
    firststep = find_linear_region(data, args.tolerance)
    
    # perform linear regression in the linear region
    (D, D_std, r2, npoints_fit) = perform_linear_regression(data, firststep)
    
    # Hummer correction
    k_hummer = calc_Hummer_correction(args.temperature, args.viscosity, args.length)
    
    # print results
    print("  \033[1mMSDiff results\033[0m")
    print(f"Diffusion coefficient: \t\t D = ({D:.2f} ± {D_std:.2f}) * 10^-12 m^2/s")
    print(f"Hummer correction term: \t K =  {k_hummer:.2f}         * 10^-12 m^2/s")
    print(f"Fit quality: \t\t\t R^2 = {r2:.4f}")
    print(f"Linear region started at \t t = {data['time'][firststep]:.4f}")
    print(f"Used {npoints_fit} points for fit.")
    
    # generate a plot if requested
    if args.plot:
        generate_simple_plot(data, firststep, args.output,)

    return 0
