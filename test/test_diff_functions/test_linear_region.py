""" 
Test the function to find the linear region of an MSD data set.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from msdiff import find_linear_region, perform_linear_regression, calc_Hummer_correction


@pytest.mark.parametrize(
    "msd_file, firststep",
    [
        (
            pd.read_csv(
                "./examples/ntf2/msd_from_travis.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            661,
        ),
        (
            pd.read_csv(
                "./examples/emim/msd_C6H11N2_#3.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            71,
        ),
    ],
)
def test_find_linear_region(
    msd_file: pd.DataFrame, firststep: int, tol: float = 0.05
) -> None:
    assert firststep == find_linear_region(msd_file, tol=tol)


@pytest.mark.parametrize(
    "msd_file, firststep, D, D_std, r2, npoints_fit",
    [
        (
            pd.read_csv(
                "./examples/ntf2/msd_from_travis.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            661,
            21.20593745,
            0.00786019,
            0.99995343,
            341,
        ),
        (
            pd.read_csv(
                "./examples/emim/msd_C6H11N2_#3.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            71,
            192.81331505,
            0.02890367,
            0.9999790,
            936,
        ),
    ],
)
def test_perform_linear_regression(
    msd_file: pd.DataFrame,
    firststep: int,
    D: float,
    D_std: float,
    r2: float,
    npoints_fit: int,
) -> None:
    assert perform_linear_regression(msd_file, firststep) == pytest.approx(
        (D, D_std, r2, npoints_fit)
    )


@pytest.mark.parametrize(
    "temperature, viscosity, box_length, k_hummer",
    [
        (298.15, 0.00787, 1234, 63.80164586),
        (350, 0.5, 10000, 0.14547387),
        (100, 0.00958, 5473, 3.96365643),
    ],
)
def test_calc_Hummer_correction(
    temperature: float, viscosity: float, box_length: float, k_hummer: float
) -> None:
    assert calc_Hummer_correction(temperature, viscosity, box_length) == pytest.approx(
        (k_hummer)
    )
