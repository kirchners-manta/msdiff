"""
Tests for transport number calculations.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from msdiff.functions import calc_transport_numbers


def test_calc_transport_numbers_matches_legacy_formulas() -> None:
    data = pd.DataFrame(
        {
            "contribution": [
                "msd_1_self",
                "msd_2_self",
                "msd_3_self",
                "msd_1_cross",
                "msd_2_cross",
                "msd_3_cross",
                "msd_1_2",
                "msd_1_3",
                "msd_2_3",
            ],
            "sigma": [1.2, 2.4, 1.8, 0.3, -0.1, 0.2, 0.5, -0.2, 0.4],
            "delta_sigma": [0.10, 0.20, 0.15, 0.05, 0.04, 0.03, 0.06, 0.02, 0.05],
        }
    )

    transport = calc_transport_numbers(data, species=3)

    self_terms = np.array([1.2, 2.4, 1.8])
    cross_terms = np.array([0.3, -0.1, 0.2])
    self_terms_err = np.array([0.10, 0.20, 0.15])
    cross_terms_err = np.array([0.05, 0.04, 0.03])
    two_body_terms = np.array(
        [
            [0.0, 0.5, -0.2],
            [0.5, 0.0, 0.4],
            [-0.2, 0.4, 0.0],
        ]
    )
    two_body_terms_err = np.array(
        [
            [0.0, 0.06, 0.02],
            [0.06, 0.0, 0.05],
            [0.02, 0.05, 0.0],
        ]
    )

    s_self = np.sum(self_terms)
    s_tot = s_self + np.sum(cross_terms) + 0.5 * np.sum(two_body_terms)
    full_terms = self_terms + cross_terms
    full_terms_err = np.sqrt(self_terms_err**2 + cross_terms_err**2)

    expected_t_ideal = np.zeros(3)
    expected_t_ideal_err = np.zeros(3)
    expected_t_real = np.zeros(3)
    expected_t_real_err = np.zeros(3)

    for i in range(3):
        expected_t_ideal[i] = self_terms[i] / s_self
        expected_t_ideal_err[i] = (
            np.sqrt(
                self_terms_err[i] ** 2
                * (sum(self_terms[j] for j in range(3) if j != i)) ** 2
                + self_terms[i] ** 2
                * sum(self_terms_err[j] ** 2 for j in range(3) if j != i)
            )
            / s_self**2
        )

        expected_t_real[i] += (self_terms[i] + cross_terms[i]) / s_tot
        for j in range(3):
            expected_t_real[i] += 0.5 * two_body_terms[i, j] / s_tot

        expected_t_real_err[i] = (
            np.sqrt(
                full_terms_err[i] ** 2
                * (
                    sum(full_terms[j] for j in range(3) if j != i)
                    + 0.5 * np.sum(two_body_terms)
                    - 0.5 * sum(two_body_terms[i, j] for j in range(3) if j != i)
                )
                ** 2
                + sum(two_body_terms_err[i, j] ** 2 for j in range(3) if j != i)
                * (
                    0.5 * (sum(full_terms) + 0.5 * np.sum(two_body_terms))
                    - full_terms[i]
                    - 0.5 * sum(two_body_terms[i, j] for j in range(3) if j != i)
                )
                ** 2
                + sum(full_terms_err[j] ** 2 for j in range(3) if j != i)
                * (
                    full_terms[i]
                    + 0.5 * sum(two_body_terms[i, j] for j in range(3) if j != i)
                )
                ** 2
                + sum(
                    two_body_terms_err[j, k] ** 2
                    for j in range(3)
                    for k in range(j + 1, 3)
                    if j != i and k != i
                )
                * (
                    full_terms[i]
                    + 0.5 * sum(two_body_terms[i, j] for j in range(3) if j != i)
                )
                ** 2
            )
            / s_tot**2
        )

    assert np.allclose(transport["t_ideal"], expected_t_ideal)
    assert np.allclose(transport["t_ideal_err"], expected_t_ideal_err)
    assert np.allclose(transport["t_real"], expected_t_real)
    assert np.allclose(transport["t_real_err"], expected_t_real_err)
