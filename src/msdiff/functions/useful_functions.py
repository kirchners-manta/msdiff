"""
Useful functions for the diffusion coefficient calculation.
"""
from __future__ import annotations

import lmfit
import numpy as np
import pandas as pd

lmod = lmfit.models.LinearModel()


def find_linear_region(data: pd.DataFrame, tol: float) -> int:
    """Find the linear region in the MSD data.

    Parameters
    ----------
    data : pd.DataFrame
        MSD data
    tol : float
        Tolerance for the slope of the linear region

    Returns
    -------
    int
        First step of the linear region, not its index
    """
    # use log-log plot to find linear region
    # drop first data point to avoid zero
    lnMSD = np.log(data["msd"][1:])
    lntime = np.log(data["time"][1:])

    # set initial values
    linear_region = True
    counter = 1
    ndata = len(lntime)

    # start from the end of the data set and go backwards
    # in increments of timestepskip
    while linear_region:
        # in the beginning, take 20% of the data set, then stepwise increase by 1%
        timestepskip = int((0.2 + counter * 0.01) * ndata)
        timestepskip_before = int((0.2 + (counter - 1) * 0.01) * ndata)

        # check if the end of the data set is reached
        # if not calculate slope between two points and check if it is within tolerance to 1
        if (timestepskip + 1) <= ndata:
            t1 = ndata - timestepskip
            t2 = ndata - timestepskip_before
            slope = (lnMSD[t1] - lnMSD[t2]) / (lntime[t1] - lntime[t2])
            if np.abs(slope - 1.0) > tol:
                linear_region = False
                firststep = t1
                return firststep
            else:
                counter += 1
        # else, exit the loop and return the last value
        else:
            linear_region = False
            return firststep

    return -1


def perform_linear_regression(
    data: pd.DataFrame, firststep: int
) -> tuple[float, float, float, int]:
    """Perform linear regression on the MSD data.

    Parameters
    ----------
    data : pd.DataFrame
        MSD data
    firststep : int
        First step of the linear region, not its index

    Returns
    -------
    tuple[float, float, float, int]
        Diffusion coefficient, its standard deviation, R^2 value and number of data points

    Raises
    ------
    ValueError
        Not enough data points for linear regression.
    Warning
        Number of data points is small.
    """
    # select data for fitting according from linear region
    msd_data = data[data["time"] >= data["time"][firststep]]
    ndata = len(msd_data)
    if ndata < 2:
        raise ValueError("Not enough data points for linear regression.")
    elif ndata < 100:
        raise Warning("Small number of data points.")

    # initial guess to improve the fit
    init = lmod.guess(data=msd_data["msd"], x=msd_data["time"])
    # perform the fit
    fit = lmod.fit(data=msd_data["msd"], x=msd_data["time"], params=init)

    # results
    D = fit.best_values["slope"] / 6
    D_std = fit.params["slope"].stderr / 6
    r2 = 1 - fit.residual.var() / np.var(msd_data["msd"])

    return D, D_std, r2, ndata


def calc_Hummer_correction(temp: float, viscosity: float, box_length: float) -> float:
    """Calculate the Hummer correction term to extrapolate the diffusion coefficient to infinite box size.

    Parameters
    ----------
    temp : float
        Temperature in K
    viscosity : float
        Dynamic viscosity in Pa s (= kg (m s)^-1)
    box_length : float
        Box length in pm

    Returns
    -------
    float
        Hummer correction term in 10^-12 m^2/s
    """
    xi = 2.837298  # dimensionless
    kb = 1.38064852e-23  # Boltzmann constant in J/K
    # calculate the Hummer correction term
    k_hummer = kb * xi * temp * 1e24 / (6 * np.pi * viscosity * box_length)

    return k_hummer
