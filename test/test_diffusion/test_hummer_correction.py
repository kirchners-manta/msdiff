"""
Test the function to calculate the Hummer correction.
"""

from __future__ import annotations

import pytest

from msdiff import calc_Hummer_correction


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
