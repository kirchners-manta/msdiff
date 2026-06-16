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
    data: pd.DataFrame,
    tol: float,
    nslice: int = 25,
    incr: float = 0.01,
) -> list[int]:
    """Find the linear region in the MSD or collective MSD data.
    The MSD data is partitioned into nslice slices, and in each slice, the slope is calculated. If the slope is about 1 within the tolerance, the slice is is gradually increased by increased until the slope is not about 1 anymore.
    The search is started at the end of the data set and goes backwards (i.e., from larger to smaller correlation times).
    After one slice is finished, the next slice is started at half the size of the previous slice. That means, effectively, there are 2 * nslice - 1 slices to check.
    The slice with the largest number of data points is selected as the linear region.

    The slope is calculated in a log-log plot, i.e., ln(MSD) vs ln(time).
    To deal with MSD data that have a notable ballistic regime at short times, the ln(MSD) is shifted so that the first data point is zero.

    Parameters
    ----------
    data : pd.DataFrame
        Input data. Has two columns: time and msd/collective msd.
    tol : float
        Tolerance for the slope of the linear region.
    nslice : int
        Number of slices to partition the data set.
    incr : float
        Increment for the linear region search.

    Returns
    -------
    list[int]
        Indices of the first and last time step of the linear region.
        Is (-1, -1) if no linear region is found.
    """

    # initialize empty list to store the intervals
    int_list = []
    # number of data points from first column (the time)
    ndata = len(data.iloc[:, 0])

    # determine the number of intervals to check
    for n in range(2 * nslice - 1):

        # define starting points for the scanning: t2 > t1
        # t2 (index) is the end of the interval (at larger correlation times)
        # t1 (index) is the beginning of the interval (at smaller correlation times)
        linear_region = True
        t1 = ndata - int((n + 2) / 2 * ndata / nslice) + 1
        t2 = ndata - int(n / 2 * ndata / nslice) - 1

        while linear_region:
            # extract region of interest from data
            region = data.iloc[t1 - 1 : t2 + 1].copy()

            # shift dataframe so that both time and MSD start from 0
            region_values = region.iloc[:, :2].astype(float)
            region.iloc[:, :2] = region_values.subtract(
                region_values.iloc[0], axis="columns"
            )

            # use log-log plot to find linear region
            lnTime = np.log(region.iloc[1:, 0])
            lnMSD = np.log(region.iloc[1:, 1])

            # calculate the slope

            # either from a two-point formula
            # not used from v 0.3.0 onwards, but kept here for reference
            # slope = (lnMSD[t1] - lnMSD[t2]) / (lnTime[t1] - lnTime[t2])

            # or from a linear regression
            slope, _, r2, _ = lmfit_linear_regression(
                lnTime, lnMSD, np.zeros_like(lnMSD)
            )

            # if the slope is nan, exit the loop
            if np.isnan(slope):  # pragma: no cover
                break
            # if the slope is not within tolerance or the R^2 value is not close to 1, exit the loop
            elif np.abs(slope - 1.0) > tol or r2 < 0.95:
                linear_region = False
            # if the slope is within tolerance and the R^2 value is close to 1, store the interval and increase it
            else:
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
                t1 -= max(1, int(ndata * incr))
                if t1 < 1:
                    linear_region = False

    linreg_data = pd.DataFrame(int_list, columns=["t1", "t2", "npoints", "slope_abs"])

    if len(linreg_data) >= 1:
        # identify the row where npoints is maximal.
        # if several rows have the same value, take the one where the slope is closest to 1
        linreg_final = linreg_data.sort_values(
            ["npoints", "slope_abs"], ascending=[False, True]
        ).iloc[[0]]
        firststep, laststep = (
            linreg_final["t1"].iloc[0],
            linreg_final["t2"].iloc[0],
        )
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
    elif ndata < 50:
        print(
            f"Info: Only {ndata} data points in the linear region. The linear regression may be unreliable.\n"
        )

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
        Uncertainties of the y-values (in this case, their standard errors). If all values are zero, a simple linear regression is performed. Otherwise, a weighted linear regression is performed.

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
        result = lmod.fit(y, params, x=x, scale_covar=False)
        r2 = float(result.rsquared)
    # if there are uncertainties, perform a weighted linear regression
    else:
        fit_weights = 1 / e
        result = lmod.fit(y, params, x=x, weights=fit_weights, scale_covar=False)

        # lmfit applies weights to the residual as (y - yhat) * weights.
        # Because we pass 1 / e here, the effective inverse-variance weights
        # are 1 / e**2 for a weighted R^2 calculation.
        weights = fit_weights**2
        weighted_mean = np.average(y, weights=weights)
        ss_res = np.sum(weights * (y - result.best_fit) ** 2)
        ss_tot = np.sum(weights * (y - weighted_mean) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return [
        float(result.params["slope"].value),
        float(result.params["slope"].stderr),
        r2,
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
    if box_length == 0:
        k_hum = delta_k_hum = 0.0
    elif viscosity == 0:
        k_hum = delta_k_hum = 0.0
        print(
            "Info: No viscosity given, set to zero. Hummer correction will be zero.\n"
        )
    else:
        k_hum = (
            KBOLTZ * ZETA_HUMMER * temp * 1e24 / (6 * np.pi * viscosity * box_length)
        )
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
    species: int,
) -> pd.DataFrame:
    """Calculate ideal and real transport numbers for each species in the system.

    Parameters
    ----------
    data : pd.DataFrame
        Contributions to the conductivity.
    species : int
        Number of species in the system.

    Returns
    -------
    pd.DataFrame
        Transport numbers.
    """

    def _propagate_ratio(
        numerator_matrix: np.ndarray,
        values: np.ndarray,
        errors: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Propagate independent uncertainties for transport numbers.

        Parameters
        ----------
        numerator_matrix : np.ndarray
            Matrix that maps the independent conductivity contributions to the
            numerator of each transport number.
        values : np.ndarray
            Values of the independent conductivity contributions.
        errors : np.ndarray
            Uncertainties of the independent conductivity contributions.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Transport numbers and their propagated uncertainties.
        """

        total = np.sum(values)
        if total == 0:
            zeros = np.zeros(numerator_matrix.shape[0])
            return zeros, zeros

        # matrix-vector product: each row of numerator_matrix selects the
        # contributions that belong to one species
        numerators = numerator_matrix @ values
        jacobian = (numerator_matrix * total - numerators[:, np.newaxis]) / total**2
        variances = (jacobian**2) @ (errors**2)
        return numerators / total, np.sqrt(np.clip(variances, 0.0, None))

    # collect all conductivity contributions once, then reshape them into arrays
    # that are easier to use for vectorized transport-number calculations
    contribution_data = data.set_index("contribution")[["sigma", "delta_sigma"]]

    self_labels = [f"msd_{i+1}_self" for i in range(species)]
    cross_labels = [f"msd_{i+1}_cross" for i in range(species)]
    pair_indices = np.triu_indices(species, k=1)
    pair_labels = [
        f"msd_{i+1}_{j+1}" for i in range(species) for j in range(i + 1, species)
    ]

    self_terms = contribution_data.loc[self_labels, "sigma"].to_numpy(dtype=float)
    cross_terms = contribution_data.loc[cross_labels, "sigma"].to_numpy(dtype=float)
    self_terms_err = contribution_data.loc[self_labels, "delta_sigma"].to_numpy(
        dtype=float
    )
    cross_terms_err = contribution_data.loc[cross_labels, "delta_sigma"].to_numpy(
        dtype=float
    )

    if pair_labels:
        pair_values = contribution_data.loc[pair_labels, "sigma"].to_numpy(dtype=float)
        pair_errors = contribution_data.loc[pair_labels, "delta_sigma"].to_numpy(
            dtype=float
        )
    else:
        pair_values = np.array([], dtype=float)
        pair_errors = np.array([], dtype=float)

    # ideal transport numbers only depend on the self terms
    t_ideal, t_ideal_err = _propagate_ratio(
        np.eye(species),
        self_terms,
        self_terms_err,
    )

    # real transport numbers use self + cross terms plus half of each pair term
    full_terms = self_terms + cross_terms
    full_terms_err = np.sqrt(self_terms_err**2 + cross_terms_err**2)

    pair_map = np.zeros((species, len(pair_values)))
    if len(pair_values) > 0:
        pair_map[pair_indices[0], np.arange(len(pair_values))] = 0.5
        pair_map[pair_indices[1], np.arange(len(pair_values))] = 0.5

    # stack one identity block for the one-body terms and one map for the
    # pair contributions so the full transport-number problem becomes linear
    t_real, t_real_err = _propagate_ratio(
        np.hstack((np.eye(species), pair_map)),
        np.concatenate((full_terms, pair_values)),
        np.concatenate((full_terms_err, pair_errors)),
    )

    # debug
    # print("t_id:", t_ideal)
    # print("t_id_err:", t_ideal_err)
    # print("t_real:", t_real)
    # print("t_real_err:", t_real_err)

    # Note to the user
    if species == 2:
        print(
            "Info: If this is truly a binary system with no other (neutral or charged) species involved, the real transport numbers are dependent on the reference frame and bear no physical meaning.\n"
        )

    # sum check
    if not np.isclose(np.sum(t_ideal), 1, atol=0.01):
        print(
            "\n*** Warning: Ideal transport numbers do not add up to 1. Please check the input data and the results.\n"
        )
    if not np.isclose(np.sum(t_real), 1, atol=0.01):
        print(
            "\n*** Warning: Real transport numbers do not add up to 1. Please check the input data and the results.\n"
        )

    # create a dataframe to store the results
    transport_numbers = pd.DataFrame(
        {
            "species": [f"{i+1}" for i in range(species)],
            "t_ideal": t_ideal,
            "t_ideal_err": t_ideal_err,
            "t_real": t_real,
            "t_real_err": t_real_err,
        }
    )

    return transport_numbers
