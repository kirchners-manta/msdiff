"""
Test the function to find the linear region of an MSD data set.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from msdiff import linear_fit


@pytest.mark.parametrize(
    "msd_data, firststep, laststep, slope, uncertainty, r2, ndata",
    [
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "diffusion_an_avg.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            111.0,
            1000.0,
            126.09698295695655,
            0.09210120779980052,
            0.9999771190107167,
            890,
        ),
        (
            pd.read_csv(
                Path(__file__).parent / "data" / "diffusion_an.csv",
                sep=";",
                skiprows=1,
                names=["time", "msd", "derivative"],
            ),
            111.0,
            1000.0,
            125.38592425600756,
            1.4496507271259767e-05,
            0.9999839597960173,
            890,
        ),
    ],
)
def test_perform_linear_regression(
    msd_data: pd.DataFrame,
    firststep: int,
    laststep: int,
    slope: float,
    uncertainty: float,
    r2: float,
    ndata: int,
) -> None:
    assert linear_fit(msd_data, firststep, laststep) == [slope, uncertainty, r2, ndata]


def test_fail_linear_regression() -> None:
    msd_file = pd.DataFrame(
        {
            "time": [1, 2, 3, 4, 5],
            "msd": [1, 2, 3, 4, 5],
            "std": [0, 0, 0, 0, 0],
        }
    )
    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        slope, uncertainty, r2, ndata = linear_fit(msd_file, 0, 4)
    assert (slope, uncertainty, r2, ndata) == (1.0, 0.3162277660049359, 1.0, 5)

    with pytest.raises(ValueError):
        linear_fit(msd_file, 0, 0)
