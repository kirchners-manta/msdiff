"""
Useful functions for the diffusion coefficient calculation.
"""

from __future__ import annotations

from typing import Any

import lmfit
import numpy as np
import pandas as pd

# constants
KBOLTZ = 1.38064852e-23  # Boltzmann constant in J/K
ZETA_HUMMER = (
    2.8372974795  # dimensionless, from https://doi.org/10.1021/acs.jpcb.3c04492
)
ZETA_ZZ = 8.1711245653  # dimensionless, from https://doi.org/10.1021/acs.jpcb.3c04492


def find_linear_region(
    data: pd.DataFrame, tol: float, nslice: int = 10, incr: float = 0.01
) -> list[int]:
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
    list[int]
        Indices of the first and last time step of the linear region.
        Is (-1, -1) if no linear region is found.
    """
    # use log-log plot to find linear region
    # drop first data point to avoid zero

    lnMSD = np.log(data.iloc[:, 1][1:])
    lnTime = np.log(data.iloc[:, 0][1:])

    # set initial values
    int_list = []
    ndata = len(lnTime)

    # determine the number of intervals to check
    for n in range(2 * nslice - 1):

        # define starting points for the scanning: t2 > t1
        # t2 (index) is the end of the interval (at larger correlation times)
        # t1 (index) is the beginning of the interval (at smaller correlation times)
        linear_region = True
        t1 = ndata - int((n + 2) / 2 * ndata / nslice) + 1
        t2 = ndata - int(n / 2 * ndata / nslice)

        while linear_region:
            # calculate the slope between two points

            slope = (lnMSD[t1] - lnMSD[t2]) / (lnTime[t1] - lnTime[t2])
            # if the slope is nan, exit the loop
            if np.isnan(slope):  # pragma: no cover
                break
            elif np.abs(slope - 1.0) > tol:
                # if the slope is not within tolerance, go to the next interval
                linear_region = False
            else:
                # if the slope is within tolerance, append the interval to the list
                # attention: t1 and t2 are indices, not time steps
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

    if len(linreg_data) >= 1:
        # identify the row where npoints is maximal.
        # if several rows have the same value, take the one where the slope is closest to 1
        linreg_final = linreg_data.sort_values(
            ["npoints", "slope_abs"], ascending=[False, True]
        ).iloc[[0]]
        firststep, laststep = linreg_final["t1"].iloc[0], linreg_final["t2"].iloc[0]
    else:
        firststep, laststep = -1, -1

    return [firststep, laststep]


def linear_fit(
    data: pd.DataFrame,
    firststep: int,
    laststep: int,
) -> list[float | int]:
    """Perform linear fit (on the MSD or collective MSD data) in the linear region.

    Parameters
    ----------
    data : pd.DataFrame
        MSD data
    firststep : int
        Index of the first step of the linear region
    laststep : int
        Index of the last step of the linear region

    Returns
    -------
    list[float | int]
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

    return lmfit_linear_regression(x, y, e)


def lmfit_linear_regression(
    x: np.ndarray[Any, np.dtype[np.float64]],
    y: np.ndarray[Any, np.dtype[np.float64]],
    e: np.ndarray[Any, np.dtype[np.float64]],
) -> list[float | int]:
    """Perform a (weighted) linear regression using the LinearModel from lmfit.

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
    list[float | int]
        Slope, its uncertainty, and the R^2 value, as well as the number of data points
    """
    # y = a * x + b
    lmod = lmfit.models.LinearModel(independent_vars=["x"])
    params = lmod.make_params()

    # perform the fit
    # if there are no uncertainties, perform a simple linear regression
    if np.all(e == 0):
        result = lmod.fit(y, params, x=x)
    # if there are uncertainties, perform a weighted linear regression
    else:
        result = lmod.fit(y, params, x=x, weights=1 / e)

    return [
        float(result.params["slope"].value),
        float(result.params["slope"].stderr),
        float(result.rsquared),
        int(len(x)),
    ]


def calc_Hummer_correction(
    temp: float,
    viscosity: float,
    box_length: float,
    delta_viscosity: float,
) -> list[float]:
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
    list[float]
        Hummer correction term and its standard deviation in m^2 s^-1
    """

    # calculate the Hummer correction term
    k_hum = KBOLTZ * ZETA_HUMMER * temp * 1e24 / (6 * np.pi * viscosity * box_length)
    delta_k_hum = (
        KBOLTZ
        * ZETA_HUMMER
        * temp
        * 1e24
        * delta_viscosity
        / (6 * np.pi * viscosity**2 * box_length)
    )

    return [k_hum, delta_k_hum]


def calc_orthoboxy_viscosity(
    diff_xy: float,
    delta_diff_xy: float,
    diff_z: float,
    delta_diff_z: float,
    temp: float,
    box_length: float,
) -> list[float]:
    """Calculate the viscosity using the Orthoboxy method.

    Parameters
    ----------
    diff_xy : float
        Diffusion coefficient in xy plane in 10^-12 m^2/s
    delta_diff_xy : float
        Uncertainty of diffusion coefficient in xy plane in 10^-12 m^2/s
    diff_z : float
        Diffusion coefficient in z direction in 10^-12 m^2/s
    delta_diff_z : float
        Uncertainty of diffusion coefficient in z direction in 10^-12 m^2/s
    temp : float
        Temperature in K
    box_length : float
        Box length in z direction in pm

    Returns
    -------
    list[float]
        Viscosity and its standard deviation in mPa s (= 10^-3 kg (m s)^-1)
    """

    # calculate the viscosity using the Orthoboxy method
    eta = (
        KBOLTZ
        * ZETA_ZZ
        * temp
        * 1e24
        / (6 * np.pi * box_length * (diff_xy - diff_z))
        * 1e3  # from Pa s to mPa s
    )
    delta_eta = (
        KBOLTZ
        * ZETA_ZZ
        * temp
        * 1e24
        / (6 * np.pi * box_length * (diff_xy - diff_z) ** 2)
        * (delta_diff_xy**2 + delta_diff_z**2) ** 0.5
    ) * 1e3

    return [eta, delta_eta]


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

    # only if contributions are not zero
    if s_ne == 0:
        ion = 0.0
        ion_err = 0.0
        t_mm_id = 0.0
        t_mm_id_err = 0.0
        t_pp_id = 0.0
        t_pp_id_err = 0.0

        # print information to user
        print(
            "\n*** Warning: Nernst-Einstein conductivity is zero, transport numbers are not calculated.\n"
        )
    else:
        # ionicity is the ratio of the total Einstein-Helfand conductivity to the total Nernst-Einstein conductivity
        ion = s_eh / s_ne
        ion_err = np.sqrt((s_eh_err / s_ne) ** 2 + (s_eh * s_ne_err / s_ne**2) ** 2)

        # the ideal transport numbers are calculated from the self terms only
        t_mm_id = s_mm_self / s_ne
        t_mm_id_err = np.sqrt(
            (s_mm_self_err / s_ne) ** 2 + (s_mm_self * s_ne_err / s_ne**2) ** 2
        )
        t_pp_id = s_pp_self / s_ne
        t_pp_id_err = np.sqrt(
            (s_pp_self_err / s_ne) ** 2 + (s_pp_self * s_ne_err / s_ne**2) ** 2
        )

    # there is no physical meaning in the transport number for the plus minus terms. it is equally attributed to both ions
    t_pm = s_pm / s_eh
    t_pm_err = np.sqrt((s_pm_err / s_eh) ** 2 + (s_pm * s_eh_err / s_eh**2) ** 2)
    t_mm = s_mm_tot / s_eh + t_pm / 2
    t_mm_err = np.sqrt(
        (s_mm_tot_err / s_eh) ** 2
        + (s_mm_tot * s_eh_err / s_eh**2) ** 2
        + (t_pm_err / 2) ** 2
    )
    t_pp = s_pp_tot / s_eh + t_pm / 2
    t_pp_err = np.sqrt(
        (s_pp_tot_err / s_eh) ** 2
        + (s_pp_tot * s_eh_err / s_eh**2) ** 2
        + (t_pm_err / 2) ** 2
    )

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
        }
    )

    return a_posteriori
