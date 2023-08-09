"""
Useful functions for the diffusion coefficient calculation.
"""
from __future__ import annotations

import lmfit
import numpy as np
import pandas as pd

lmod = lmfit.models.LinearModel()

def find_linear_region(data: pd.DataFrame, tol: float) -> int:
    
    # use log-log plot to find linear region
    # drop first data point to avoid zero
    lnMSD = np.log(data["msd"][1:])
    lntime = np.log(data["time"][1:])

    # set initial values
    linear_region = True
    timestepskip = 100
    counter = 1
    ndata = len(lntime)
    
    # start from the end of the data set and go backwards
    # in increments of timestepskip
    while linear_region:
        # check if the end of the data set is reached
        if counter * timestepskip + 1 > ndata:
            firststep = ndata - 1 - (counter - 1) * timestepskip
            linear_region = False
            return firststep
        # calculate slope between two points and check if it is within tolerance to 1
        else:
            t1 = ndata - 1 - (counter - 1) * timestepskip
            t2 = ndata - 1 - counter * timestepskip
            slope = (lnMSD[t1] - lnMSD[t2]) / (lntime[t1] - lntime[t2])
            if np.abs(slope - 1.) > tol:
                linear_region = False
                firststep = t1
                return firststep
            else:
                counter += 1

def perform_linear_regression(data: pd.DataFrame, firststep: int) -> tuple[float, float, float, int]:

    # select data for fitting according from linear region
    msd_data = data[data["time"] >= data["time"][firststep]]
    ndata = len(msd_data)
    if ndata < 2:
        raise ValueError("Not enough data points for linear regression.")
    elif ndata < 100:
        print(f"Warning: Small number ({ndata}) of data points.")

    # initial guess to improve the fit
    init = lmod.guess(data=msd_data["msd"], x=msd_data["time"])
    # perform the fit
    fit = lmod.fit(data=msd_data["msd"], x=msd_data["time"], params=init)
    
    # results
    D = fit.best_values["slope"] / 6
    D_std = fit.params["slope"].stderr / 6
    r2 = 1 - fit.residual.var() / np.var(msd_data["msd"]) 

    return D, D_std, r2, ndata

def calc_Hummer_correction(temp: float, viscosity:float, box_length: float) -> float:

    xi = 2.837298  # dimensionless
    kb = 1.38064852e-23  # Boltzmann constant in J/K
    # calculate the Hummer correction term
    k_hummer = kb * xi * temp * 1e24 / (6 * np.pi * viscosity * box_length)

    return k_hummer
