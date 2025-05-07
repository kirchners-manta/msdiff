"""
Test the function to calculate the viscosity in the OrthoBoXY formalism.
"""

from __future__ import annotations

import pytest

from msdiff import calc_orthoboxy_viscosity


@pytest.mark.parametrize(
    "diff_xy, delta_diff_xy, diff_z, delta_diff_z, temp, box_length, eta, delta_eta",
    [
        (
            5417.100506285782,
            2.5839055779363327,
            4044.697510637169,
            2.689415842722207,
            330.0,
            4950.97,
            0.2906737593912252,
            0.00078991494279918,
        )
    ],
)
def test_calc_orthoboxy_viscosity(
    diff_xy: float,
    delta_diff_xy: float,
    diff_z: float,
    delta_diff_z: float,
    temp: float,
    box_length: float,
    eta: float,
    delta_eta: float,
) -> None:
    assert calc_orthoboxy_viscosity(
        diff_xy, delta_diff_xy, diff_z, delta_diff_z, temp, box_length
    ) == pytest.approx([eta, delta_eta])
