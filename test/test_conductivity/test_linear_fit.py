"""
Tests for weighted conductivity linear fits.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from msdiff.conductivity.ionic_conductivity import read_input_conductivity
from msdiff.functions import find_linear_region, linear_fit


def test_weighted_conductivity_fit_uses_inverse_variance_r2() -> None:
    data_file = (
        Path(__file__).parents[2]
        / "examples"
        / "conductivity"
        / "3_comp"
        / "conduct_3comp.csv"
    )

    data = read_input_conductivity(str(data_file), uncert="var", species=3)
    firststep, laststep = find_linear_region(data[["time", "total_eh"]], 0.10)

    slope, uncertainty, r2, ndata = linear_fit(
        data[["time", "msd_1_cross", "msd_1_cross_std"]],
        firststep,
        laststep,
    )

    assert ndata == 399
    assert slope == pytest.approx(-0.010091151099650756)
    assert uncertainty == pytest.approx(0.0022738762646958774)
    assert r2 == pytest.approx(0.11382236185625505)
