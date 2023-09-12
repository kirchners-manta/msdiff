""" 
Test the function to find the linear region of an MSD data set.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from msdiff import (
    calc_Hummer_correction,
    find_linear_region,
    get_diffusion_coefficient,
    find_cond_region,
    get_conductivity,
)


@pytest.mark.parametrize(
    "msd_file, mol_index, tol, firststep",
    [
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "msd_ntf2.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd_1", "derivative"],
            ),
            0,
            0.05,
            661,
        ),
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "msd_emim.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd_4", "derivative"],
            ),
            3,
            0.07,
            51,
        ),
    ],
)
def test_find_linear_region(
    msd_file: pd.DataFrame,
    mol_index: int,
    tol: float,
    firststep: int,
) -> None:
    assert firststep == find_linear_region(msd_file, mol_index, tol)


@pytest.mark.parametrize(
    "msd_file, mol_index, tol",
    [
        (
            pd.DataFrame(
                {
                    "time": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    "msd_1": [
                        1,
                        4,
                        9,
                        16,
                        25,
                        36,
                        49,
                        64,
                        81,
                        100,
                        121,
                        144,
                        169,
                        196,
                        225,
                    ],
                }
            ),
            0,
            0.05,
        )
    ],
)
def test_no_lin_reg_found(
    msd_file: pd.DataFrame,
    mol_index: int,
    tol: float,
) -> None:
    with pytest.raises(ValueError):
        find_linear_region(msd_file, mol_index, tol)


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
    "msd_file, mol_index, firststep, temp, viscosity, box_length, delta_viscosity, diff_coeff, delta_diff_coeff, r2, npoints_fit, k_hummer, delta_k_hummer",
    [
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "msd_ntf2.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd_1", "derivative"],
            ),
            0,
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
                names=["time", "msd_3", "derivative"],
            ),
            2,
            71,
            350,
            0.5,
            10000,
            0.0000,
            192.81331505,
            0.02890367,
            0.9999790,
            936,
            None,
            None,
        ),
    ],
)
def test_perform_linear_regression(
    msd_file: pd.DataFrame,
    mol_index: int,
    firststep: int,
    temp: float,
    viscosity: float,
    box_length: float,
    delta_viscosity: float,
    diff_coeff: float,
    delta_diff_coeff: float,
    r2: float,
    npoints_fit: int,
    k_hummer: float | None,
    delta_k_hummer: float | None,
) -> None:
    assert get_diffusion_coefficient(
        msd_file, mol_index, firststep, temp, viscosity, box_length, delta_viscosity
    ) == pytest.approx(
        (diff_coeff, delta_diff_coeff, r2, npoints_fit, k_hummer, delta_k_hummer)
    )


def test_fail_linear_regression() -> None:
    msd_file = pd.DataFrame(
        {
            "time": [1, 2, 3, 4, 5],
            "msd_1": [1, 2, 3, 4, 5],
            "derivative": [1, 1, 1, 1, 1],
        }
    )
    with pytest.raises(Warning):
        get_diffusion_coefficient(msd_file, 0, 1, 201, 0.007, 5000, 0.0001)

    with pytest.raises(ValueError):
        get_diffusion_coefficient(msd_file, 0, 4, 201, 0.007, 5000, 0.0001)


def test_neg_mol_index() -> None:
    msd_file = pd.read_csv(
        Path(__file__).parent / "data" / "msd_emim.csv",
        sep=";",
        skiprows=1,
        names=["time", "msd_-3", "derivative"],
    )
    with pytest.raises(ValueError):
        get_diffusion_coefficient(msd_file, -4, 300, 201, 0.007, 5000, 0.0001)


@pytest.mark.parametrize(
    "cond_data, tskip, tol, firststep, laststep",
    [
        (
            pd.DataFrame(
                {
                    "time": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                    "cond": [
                        1,
                        4,
                        9,
                        16,
                        25,
                        36,
                        49,
                        64,
                        81,
                        100,
                        121,
                        144,
                        169,
                        196,
                        225,
                    ],
                }
            ),
            0.1,
            0.1,
            -1,
            -1,
        )
    ],
)
def test_no_cond_region(
    cond_data: pd.DataFrame, tskip: float, tol: float, firststep: int, laststep: int
) -> None:
    """Test if the linear region is found in the conductivity data."""

    assert find_cond_region(cond_data, tskip, tol) == (-1, -1)
