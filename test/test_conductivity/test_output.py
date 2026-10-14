"""
Tests for the conductivity result output and the conductivity error paths.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pytest

from msdiff.conductivity import calculate_conductivity
from msdiff.conductivity.output import (
    print_program_header,
    print_results_to_file,
    print_results_to_stdout,
)
from msdiff.functions import calc_transport_numbers


def _contributions(self_terms: list[float]) -> pd.DataFrame:
    labels = ["msd_1_self", "msd_2_self", "msd_1_cross", "msd_2_cross", "msd_1_2"]
    sigma = [*self_terms, 0.0, 0.0, 0.0]
    return pd.DataFrame(
        {"contribution": labels, "sigma": sigma, "delta_sigma": [0.01] * len(labels)}
    )


def test_output_files_and_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    results = pd.DataFrame(
        {
            "contribution": ["msd_1_self", "total_eh"],
            "sigma": [1.0, 2.0],
            "delta_sigma": [0.1, 0.2],
            "r2": [0.99, 0.98],
            "t_start": [10.0, 10.0],
            "t_end": [100.0, 100.0],
            "n_data": [91, 91],
        }
    )
    transport = pd.DataFrame(
        {
            "species": ["1", "2"],
            "t_ideal": [0.5, 0.5],
            "t_ideal_err": [0.01, 0.01],
            "t_real": [0.4, 0.6],
            "t_real_err": [0.02, 0.02],
        }
    )

    print_program_header()
    print_results_to_stdout(results, transport)
    print_results_to_file(results, transport, str(tmp_path / "cond"))

    out = capsys.readouterr().out
    assert "MSDiff Conductivity" in out
    assert "Linear regime identified between 10.00 ps and 100.00 ps" in out

    written = pd.read_csv(tmp_path / "cond_out.csv", skipinitialspace=True)
    assert written["sigma / S*m^-1"].tolist() == pytest.approx([1.0, 2.0])
    tp = pd.read_csv(tmp_path / "cond_tp.csv", skipinitialspace=True)
    assert tp["t_real"].tolist() == pytest.approx([0.4, 0.6])


def test_transport_numbers_warn_if_sum_is_not_one(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # a negative self term makes the ideal transport numbers sum to 1 anyway,
    # so use a vanishing total to hit the zero branch and check no crash occurs
    transport = calc_transport_numbers(_contributions([0.0, 0.0]), 2)

    assert transport["t_ideal"].tolist() == [0.0, 0.0]
    assert transport["t_real_err"].tolist() == [0.0, 0.0]

    out = capsys.readouterr().out
    assert "reference frame" in out
    assert "Ideal transport numbers do not add up to 1" in out
    assert "Real transport numbers do not add up to 1" in out


def test_conductivity_without_linear_region(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    file = (
        Path(__file__).parents[1] / "test_cli" / "data" / "conductivity_test_data.csv"
    )
    args = argparse.Namespace(
        file=str(file),
        uncertainty="none",
        species=2,
        tolerance=0.1,
        output=str(tmp_path / "cond"),
    )
    # (-1, -1) is the documented "nothing found" return value of the search
    monkeypatch.setattr(
        "msdiff.conductivity.ionic_conductivity.find_linear_region",
        lambda *a, **kw: [-1, -1],
    )

    with pytest.raises(ValueError, match="No linear region found"):
        calculate_conductivity(args)
    assert not (tmp_path / "cond_out.csv").exists()
