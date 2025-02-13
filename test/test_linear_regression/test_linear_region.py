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
    ],
)
def test_find_linear_region(
    msd_file: pd.DataFrame,
    tol: float,
    firststep: float,
    laststep: float,
) -> None:
    assert firststep, laststep == find_linear_region(msd_file, tol)
