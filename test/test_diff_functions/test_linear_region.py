""" 
Test the function to find the linear region of an MSD data set.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from msdiff import calc_Hummer_correction, find_linear_region, get_diffusion_coefficient


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
    "temperature, viscosity, box_length, delta_viscosity, k_hummer, delta_k_hummer",
    [
        (298.15, 0.00787, 1234, 0.00018, 63.80164586, 1.45924984),
        (350, 0.5, 10000, 0.0000, 0.14547387, 0.0000),
        (201, 0.00958, 5473, 0.00001, 7.96694943, 0.00831623),
    ],
)
def test_calc_Hummer_correction(
    temperature: float,
    viscosity: float,
    box_length: float,
    delta_viscosity: float,
    k_hummer: float,
    delta_k_hummer: float,
) -> None:
    assert calc_Hummer_correction(
        temperature, viscosity, box_length, delta_viscosity
    ) == pytest.approx((k_hummer, delta_k_hummer))


@pytest.mark.parametrize(
    "msd_file, firststep, temp, viscosity, box_length, delta_viscosity, diff_coeff, delta_diff_coeff, r2, npoints_fit, k_hummer, delta_k_hummer",
    [
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "msd_ntf2.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            661,
            298.15,
            0.00787,
            1234,
            0.00018,
            21.20593745,
            0.00786019,
            0.99995343,
            341,
            63.80164586,
            1.45924984,
        ),
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "msd_emim.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            71,
            350,
            0.5,
            10000,
            0.0000,
            192.81331505,
            0.02890367,
            0.9999790,
            936,
            0.14547387,
            0.0000,
        ),
    ],
)
def test_perform_linear_regression(
    msd_file: pd.DataFrame,
    firststep: int,
    temp: float,
    viscosity: float,
    box_length: float,
    delta_viscosity: float,
    diff_coeff: float,
    delta_diff_coeff: float,
    r2: float,
    npoints_fit: int,
    k_hummer: float,
    delta_k_hummer: float,
) -> None:
    assert get_diffusion_coefficient(
        msd_file, firststep, temp, viscosity, box_length, delta_viscosity
    ) == pytest.approx(
        (diff_coeff, delta_diff_coeff, r2, npoints_fit, k_hummer, delta_k_hummer)
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
        get_diffusion_coefficient(msd_file, 1, 200, 0.007, 5000, 0.0001)

    with pytest.raises(ValueError):
        get_diffusion_coefficient(msd_file, 4, 200, 0.007, 5000, 0.0001)
