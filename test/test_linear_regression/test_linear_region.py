"""
Test the function to find the linear region of an MSD data set.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from msdiff import find_linear_region


@pytest.mark.parametrize(
    "msd_file, tol, firststep, laststep",
    [
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "msd_ntf2.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ).drop(columns=["derivative"]),
            0.05,
            392.0,
            1001.0,
        ),
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "msd_emim.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ).drop(columns=["derivative"]),
            0.07,
            17.0,
            1006.0,
        ),
        (
            pd.DataFrame(
                {
                    "time": np.arange(1, 100),
                    "msd": np.arange(1, 100) ** 2,
                }
            ),
            0.1,
            -1,
            -1,
        ),
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "linear_function.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            0.03,
            2,
            10000,
        ),
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "step_function.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            0.05,
            -1,
            -1,
        ),
    ],
)
def test_find_linear_region(
    msd_file: pd.DataFrame,
    tol: float,
    firststep: float,
    laststep: float,
) -> None:
    assert firststep, laststep == find_linear_region(msd_file, tol)


def test_find_linear_region_flat_data_returns_no_region() -> None:
    # a flat MSD would give log(0) after shifting the first point to zero
    data = pd.DataFrame({"time": np.arange(1.0, 201.0), "msd": np.ones(200)})

    assert find_linear_region(data, 0.1) == [-1, -1]


def test_find_linear_region_short_data_warns_instead_of_crashing() -> None:
    # 30 points / 25 slices: the smallest slices have one or two points, which
    # used to crash inside lmfit
    time = np.arange(1.0, 31.0)
    data = pd.DataFrame({"time": time, "msd": 2.0 * time})

    with pytest.warns(UserWarning, match="--slice"):
        result = find_linear_region(data, 0.1)

    assert len(result) == 2


def test_find_linear_region_short_data_with_adapted_slices_is_quiet(
    recwarn: pytest.WarningsRecorder,
) -> None:
    time = np.arange(1.0, 31.0)
    data = pd.DataFrame({"time": time, "msd": 2.0 * time})

    first, last = find_linear_region(data, 0.1, nslice=5)

    assert 0 < first < last
    assert not [w for w in recwarn if issubclass(w.category, UserWarning)]
