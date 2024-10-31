"""
Useful functions for the diffusion coefficient calculation.
"""

from __future__ import annotations

from typing import Any

import lmfit  # type: ignore
import numpy as np
import pandas as pd  # type: ignore

lmod = lmfit.models.LinearModel()


def find_linear_region(
    data: pd.DataFrame, tol: float, nslice: int = 10, incr: float = 0.01
) -> tuple[float, float]:
    """Find the linear region in the MSD or collective MSD data.
    The MSD data is partitioned into nslice slices, and in each slice, the slope is calculated. If the slope is about 1 within the tolerance, the slice is is gradually increased by incr until the slope is not about 1 anymore.
    The search is started at the end of the data set and goes backwards (i.e., from larger to smaller correlation times).
    After one slice is finished, the next slice is started at half the size of the previous slice. That means, effectively, there are 2 * nslice - 1 slices to check.
    The slice with the largest number of data points is selected as the linear region.

    Parameters
    ----------
    data : pd.DataFrame
        Input data. Has two columns: time and msd/collective msd.
    tol : float
        Tolerance for the slope of the linear region.
    nslice : int
        Number of slices to partition the data set, default is 10.
    incr : float
        Increment for the linear region search, default is 0.01.

    Returns
    -------
    tuple[float, float]
        First and last time step of the linear region, not their indices. Is (-1, -1) if no linear region is found.
    """
    # use log-log plot to find linear region
    # drop first data point to avoid zero
    lnMSD = np.log(data.iloc[:, 1])[1:]
    lnTime = np.log(data.iloc[:, 0])[1:]

    # set initial values
    int_list = []
    ndata = len(lnTime)

    # determine the number of intervals to check
    for n in range(2 * nslice - 1):

        # define starting points for the scanning: t2 > t1
        # t2 is the end of the interval (at larger correlation times)
        # t1 is the beginning of the interval (at smaller correlation times)
        linear_region = True
        t1 = ndata - int((n + 2) / 2 * ndata / nslice) + 1
        t2 = ndata - int(n / 2 * ndata / nslice)

        # debug
        # print(t1, t2)

        while linear_region:
            # calculate the slope between two points

            # debug
            # print(t1, t2)

            slope = (lnMSD[t1] - lnMSD[t2]) / (lnTime[t1] - lnTime[t2])
            # if the slope is nan, exit the loop
            if np.isnan(slope):
                break
            elif np.abs(slope - 1.0) > tol:
                # if the slope is not within tolerance, go to the next interval
                linear_region = False
            else:
                # if the slope is within tolerance, append the interval to the list
                int_list.append(
                    [
                        t1,
                        t2,
                        t2 - t1,
                        np.abs((lnMSD[t1] - lnMSD[t2]) / (lnTime[t1] - lnTime[t2]) - 1),
                    ]
                )
                # increase the interval by incr, but make sure t1 > 0
                t1 -= int(ndata * incr)
                if t1 < 1:
                    linear_region = False

    linreg_data = pd.DataFrame(int_list, columns=["t1", "t2", "npoints", "slope_abs"])

    if len(linreg_data) > 1:
        # identify the row where npoints is maximal.
        # if several rows have the same value, take the one where the slope is closest to 1
        linreg_final = linreg_data.sort_values(
            ["npoints", "slope_abs"], ascending=[False, True]
        ).iloc[[0]]
        firststep, laststep = linreg_final["t1"].iloc[0], linreg_final["t2"].iloc[0]
    elif len(linreg_data) == 1:
        firststep, laststep = linreg_data["t1"].iloc[0], linreg_data["t2"].iloc[0]
    else:
        firststep, laststep = -1, -1

    return firststep, laststep


def linear_fit(
    data: pd.DataFrame,
    firststep: float,
    laststep: float,
) -> tuple[float, float, float, int]:
    """Perform linear fit (on the MSD or collective MSD data) in the linear region.

    Parameters
    ----------
    data : pd.DataFrame
        MSD data
    firststep : float
        First step of the linear region, not its index
    laststep : float
        Last step of the linear region, not its index

    Returns
    -------
    tuple[float, float, float, int]
        slope, its uncertainty, R^2 value, and the number of data points

    Raises
    ------
    ValueError
        Not enough data points for linear regression.
    Warning
        Number of data points is small.
    """
    # select data for fitting according to linear region
    fit_data = data[
        (data["time"] >= data["time"][firststep])
        & (data["time"] <= data["time"][laststep])
    ]
    ndata = len(fit_data)
    if ndata < 2:
        raise ValueError("Not enough data points for linear regression.")
    elif ndata < 100:
        raise Warning("Small number of data points.")

    # perform a linear regression with or without weighted errors, depending on the uncertainties

    x = fit_data.iloc[:, 0]
    y = fit_data.iloc[:, 1]
    e = fit_data.iloc[:, 2]

    if np.all(e == 0):
        # no uncertainties, perform a simple linear regression
        return linear_regression(x, y)

    else:
        # uncertainties are given, perform a weighted linear regression
        return weighted_linear_regression(x, y, e)


def linear_regression(
    x: np.ndarray[Any, np.dtype[np.float64]],
    y: np.ndarray[Any, np.dtype[np.float64]],
) -> tuple[float, float, float, int]:
    """Perform a linear regression.

    Parameters
    ----------
    x : np.ndarray
        x-values
    y : np.ndarray
        y-values

    Returns
    -------
    tuple[float, float, float, int]
        Slope, its uncertainty, and the R^2 value as well as the number of data points
    """
    # no uncertainties, perform a simple linear regression
    # y = a * x + b

    ndata = len(x)

    a = (ndata * np.sum(x * y) - np.sum(x) * np.sum(y)) / (
        ndata * np.sum(x**2) - np.sum(x) ** 2
    )

    b = (np.sum(x**2) * np.sum(y) - np.sum(x) * np.sum(x * y)) / (
        ndata * np.sum(x**2) - np.sum(x) ** 2
    )

    da = np.sqrt(ndata / (ndata * np.sum(x**2) - np.sum(x) ** 2)) * np.sqrt(
        np.sum((y - a * x - b) ** 2) / (ndata - 2)
    )

    r2 = 1 - np.sum((y - a * x - b) ** 2) / np.sum((y - np.mean(y)) ** 2)

    return a, da, r2, ndata


def weighted_linear_regression(
    x: np.ndarray[Any, np.dtype[np.float64]],
    y: np.ndarray[Any, np.dtype[np.float64]],
    e: np.ndarray[Any, np.dtype[np.float64]],
) -> tuple[float, float, float, int]:
    """Perform a weighted linear regression.

    Parameters
    ----------
    x : np.ndarray
        x-values
    y : np.ndarray
        y-values
    e : np.ndarray
        Uncertainties of the y-values

    Returns
    -------
    tuple[float, float, float, int]
        Slope, its uncertainty, and the R^2 value, as well as the number of data points
    """
    # perform a weighted linear regression according to: https://cbe.udel.edu/wp-content/uploads/2019/03/FittingData.pdf
    # y = a * x + b

    a = (
        np.sum(x / e**2) * np.sum(y / e**2) - np.sum(x * y / e**2) * np.sum(1 / e**2)
    ) / (np.sum(x / e**2) ** 2 - np.sum(x**2 / e**2) * np.sum(1 / e**2))

    b = (np.sum(x * y / e**2) - a * np.sum(x**2 / e**2)) / np.sum(x / e**2)

    da = np.sqrt(
        np.sum(1 / e**2)
        / (np.sum(x**2 / e**2) * np.sum(1 / e**2) - np.sum(x / e**2) ** 2)
    )

    r2 = 1 - np.sum((y - a * x - b) ** 2) / np.sum((y - np.mean(y)) ** 2)

    return a, da, r2, len(x)


def calc_Hummer_correction(
    temp: float,
    viscosity: float,
    box_length: float,
    delta_viscosity: float,
) -> tuple[float, float]:
    """Calculate the Hummer correction term to extrapolate the diffusion coefficient to infinite box size, assuming that the box is an isotropic cube.

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


def calc_transport_numbers(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate the a posteriori quantities for the transport numbers and ionicity.

    Parameters
    ----------
    data : pd.DataFrame
        Results of the conductivity calculation i.e., the contributions to the conductivity.

    Returns
    -------
    pd.DataFrame
        A posteriori quantities for the transport numbers and ionicity.
    """

    # s = sigma, eh = Einstein-Helfand (all terms), ne = Nernst-Einstein (just self terms)
    # err = error
    # mm = minus minus, pp = plus plus, pm = plus minus
    # t = transport number, ion = ionicity, id = ideal

    s_eh = data.loc[data["contribution"] == "total_eh", "sigma"].values[0]
    s_eh_err = data.loc[data["contribution"] == "total_eh", "delta_sigma"].values[0]
    s_ne = data.loc[data["contribution"] == "total_ne", "sigma"].values[0]
    s_ne_err = data.loc[data["contribution"] == "total_ne", "delta_sigma"].values[0]
    s_mm_tot = data.loc[data["contribution"] == "anion_tot", "sigma"].values[0]
    s_mm_tot_err = data.loc[data["contribution"] == "anion_tot", "delta_sigma"].values[
        0
    ]
    s_mm_self = data.loc[data["contribution"] == "anion_self", "sigma"].values[0]
    s_mm_self_err = data.loc[
        data["contribution"] == "anion_self", "delta_sigma"
    ].values[0]
    s_pp_tot = data.loc[data["contribution"] == "cation_tot", "sigma"].values[0]
    s_pp_tot_err = data.loc[data["contribution"] == "cation_tot", "delta_sigma"].values[
        0
    ]
    s_pp_self = data.loc[data["contribution"] == "cation_self", "sigma"].values[0]
    s_pp_self_err = data.loc[
        data["contribution"] == "cation_self", "delta_sigma"
    ].values[0]
    s_pm = data.loc[data["contribution"] == "anion_cation", "sigma"].values[0]
    s_pm_err = data.loc[data["contribution"] == "anion_cation", "delta_sigma"].values[0]

    # calculate a posteriori quantities
    ion = s_eh / s_ne
    ion_err = np.sqrt((s_eh_err / s_ne) ** 2 + (s_eh * s_ne_err / s_ne**2) ** 2)

    t_mm_id = s_mm_self / s_ne
    t_mm_id_err = np.sqrt(
        (s_mm_self_err / s_ne) ** 2 + (s_mm_self * s_ne_err / s_ne**2) ** 2
    )
    t_mm = s_mm_tot / s_eh
    t_mm_err = np.sqrt(
        (s_mm_tot_err / s_eh) ** 2 + (s_mm_tot * s_eh_err / s_eh**2) ** 2
    )

    t_pp_id = s_pp_self / s_ne
    t_pp_id_err = np.sqrt(
        (s_pp_self_err / s_ne) ** 2 + (s_pp_self * s_ne_err / s_ne**2) ** 2
    )
    t_pp = s_pp_tot / s_eh
    t_pp_err = np.sqrt(
        (s_pp_tot_err / s_eh) ** 2 + (s_pp_tot * s_eh_err / s_eh**2) ** 2
    )

    t_pm = s_pm / s_eh
    t_pm_err = np.sqrt((s_pm_err / s_eh) ** 2 + (s_pm * s_eh_err / s_eh**2) ** 2)

    # put the a posteriori quantities to a new data frame
    a_posteriori = pd.DataFrame(
        data=[
            [
                ion,
                ion_err,
                t_mm_id,
                t_mm_id_err,
                t_pp_id,
                t_pp_id_err,
                t_mm,
                t_mm_err,
                t_pp,
                t_pp_err,
                t_pm,
                t_pm_err,
            ]
        ],
        columns=[
            "ionicity",
            "ionicity_err",
            "t_mm_ideal",
            "t_mm_ideal_err",
            "t_pp_ideal",
            "t_pp_ideal_err",
            "t_mm",
            "t_mm_err",
            "t_pp",
            "t_pp_err",
            "t_pm",
            "t_pm_err",
        ],
    ).astype(
        {
            "ionicity": float,
            "ionicity_err": float,
            "t_mm_ideal": float,
            "t_mm_ideal_err": float,
            "t_pp_ideal": float,
            "t_pp_ideal_err": float,
            "t_mm": float,
            "t_mm_err": float,
            "t_pp": float,
            "t_pp_err": float,
            "t_pm": float,
            "t_pm_err": float,
        }
    )

    return a_posteriori
