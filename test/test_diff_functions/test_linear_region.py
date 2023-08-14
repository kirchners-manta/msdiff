""" 
Test the function to find the linear region of an MSD data set.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from msdiff import calc_Hummer_correction, find_linear_region, perform_linear_regression


@pytest.mark.parametrize(
    "msd_file, firststep",
    [
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "msd_ntf2.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            661,
        ),
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "msd_emim.csv",
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
                Path(__file__).parent / "data" / "msd_ntf2.csv",
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
                Path(__file__).parent / "data" / "msd_emim.csv",
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


def test_fail_linear_regression() -> None:
    msd_file = pd.DataFrame(
        {
            "time": [1, 2, 3, 4, 5],
            "msd": [1, 2, 3, 4, 5],
            "derivative": [1, 1, 1, 1, 1],
        }
    )
    with pytest.raises(Warning):
        perform_linear_regression(msd_file, 1)

    with pytest.raises(ValueError):
        perform_linear_regression(msd_file, 4)


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
