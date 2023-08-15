"""
Useful functions for the diffusion coefficient calculation.
"""
from __future__ import annotations

import lmfit
import numpy as np
import pandas as pd

lmod = lmfit.models.LinearModel()


def find_linear_region(data: pd.DataFrame, mol_index: int, tol: float) -> int:
    """Find the linear region in the MSD data.

    Parameters
    ----------
    data : pd.DataFrame
        MSD data
    mol_index : int
        Index of the data set, i.e., the molecule
    tol : float
        Tolerance for the slope of the linear region

    Returns
    -------
    int
        First step of the linear region, not its index
    """
    # use log-log plot to find linear region
    # drop first data point to avoid zero
    lnMSD = np.log(data[f"msd_{mol_index+1}"][1:])
    lntime = np.log(data["time"][1:])

    # set initial values
    linear_region = True
    counter = 1
    ndata = len(lntime)
    firststep = -1

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

    return firststep


def calc_Hummer_correction(
    temp: float,
    viscosity: float,
    box_length: float,
    delta_viscosity: float,
) -> tuple[float, float]:
    """Calculate the Hummer correction term to extrapolate the diffusion coefficient to infinite box size.

    Parameters
    ----------
    temp : float
        Temperature in K
    viscosity : float
        Dynamic viscosity in Pa s (= kg (m s)^-1)
    box_length : float
        Box length in pm
    delta_viscosity : float
        Reported experimental error in viscosity in Pa s (= kg (m s)^-1)

    Returns
    -------
    tuple[float, float]
        Hummer correction term and its standard deviation in m^2 s^-1
    """
    xi = 2.837298  # dimensionless
    kb = 1.38064852e-23  # Boltzmann constant in J/K

    # calculate the Hummer correction term
    k_hum = kb * xi * temp * 1e24 / (6 * np.pi * viscosity * box_length)
    delta_k_hum = (
        kb
        * xi
        * temp
        * 1e24
        * delta_viscosity
        / (6 * np.pi * viscosity**2 * box_length)
    )

    return k_hum, delta_k_hum


def get_diffusion_coefficient(
    data: pd.DataFrame,
    mol_index: int,
    firststep: int,
    temp: float,
    viscosity: float,
    box_length: float,
    delta_viscosity: float,
) -> tuple[float, float, float, int, float | None, float | None]:
    """Perform linear regression on the MSD data.

    Parameters
    ----------
    data : pd.DataFrame
        MSD data
    mol_index : int
        Index of the data set, i.e., the molecule
    firststep : int
        First step of the linear region, not its index
    temp : float
        Temperature in K
    viscosity : float
        Dynamic viscosity in Pa s (= kg (m s)^-1)
    box_length : float
        Box length in pm
    delta_viscosity : float
        Reported experimental error in viscosity in Pa s (= kg (m s)^-1)

    Returns
    -------
    tuple[float, float, float, int, float | None, float | None]
        Diffusion coefficient, its standard error, R^2 value and number of data points, Hummer correction term and its standard deviation. The latter two are only returned for the first molecule because they are the same for all molecules.

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
    init = lmod.guess(data=msd_data[f"msd_{mol_index+1}"], x=msd_data["time"])
    # perform the fit
    out = lmod.fit(data=msd_data[f"msd_{mol_index+1}"], x=msd_data["time"], params=init)

    # results
    diff_coeff = out.best_values["slope"] / 6
    delta_diff_coeff = out.params["slope"].stderr / 6
    r2 = 1 - out.residual.var() / np.var(msd_data[f"msd_{mol_index+1}"])  # type: ignore

    if mol_index == 0:
        k_hum, delta_k_hum = calc_Hummer_correction(
            temp,
            viscosity,
            box_length,
            delta_viscosity,
        )
    elif mol_index > 0:
        k_hum = None
        delta_k_hum = None

    return diff_coeff, delta_diff_coeff, r2, ndata, k_hum, delta_k_hum
