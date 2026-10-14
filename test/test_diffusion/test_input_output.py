"""
Tests for reading diffusion input files and writing diffusion results.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from msdiff.diffusion.diff_coeff import read_input_diffusion
from msdiff.diffusion.output import (
    print_program_header,
    print_results_to_file,
    print_results_to_stdout,
)


def _write(path: Path, rows: list[str]) -> str:
    path.write_text("# header\n" + "\n".join(rows) + "\n", encoding="utf8")
    return str(path)


def test_read_input_none_drops_extra_columns(tmp_path: Path) -> None:
    # TRAVIS appends a derivative column, which must be dropped
    file = _write(tmp_path / "msd.csv", ["0;0;5", "1;2;5", "2;4;5"])

    data = read_input_diffusion(file, "none", 1)

    assert list(data.columns) == ["time", "msd_1_self", "msd_1_self_std"]
    assert data["msd_1_self"].tolist() == [0.0, 2.0, 4.0]
    assert (data["msd_1_self_std"] == 0.0).all()


def test_read_input_std_and_var(tmp_path: Path) -> None:
    file = _write(tmp_path / "msd.csv", ["0;0;0;0;0", "1;2;4;3;9", "2;4;16;6;25"])

    std = read_input_diffusion(file, "std", 2)
    assert list(std.columns) == [
        "time",
        "msd_1_self",
        "msd_1_self_std",
        "msd_2_self",
        "msd_2_self_std",
    ]
    assert std["msd_1_self_std"].tolist() == [0.0, 4.0, 16.0]

    # variances are converted to standard deviations
    var = read_input_diffusion(file, "var", 2)
    assert var["msd_1_self_std"].tolist() == [0.0, 2.0, 4.0]
    assert var["msd_2_self_std"].tolist() == [0.0, 3.0, 5.0]


def test_read_input_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_input_diffusion(str(tmp_path / "missing.csv"), "none", 1)


@pytest.fixture
def results() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "diffusion_coefficient": [1.5],
            "delta_diffusion_coefficient": [0.1],
            "k_hummer": [0.2],
            "delta_k_hummer": [0.02],
            "r2": [0.999],
            "t_fit_start": [10.0],
            "t_fit_end": [100.0],
            "n_data": [91],
        }
    )


def test_output_without_orthoboxy(
    results: pd.DataFrame, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    print_program_header()
    print_results_to_stdout(results)
    print_results_to_file(results, str(tmp_path / "res"))

    out = capsys.readouterr().out
    assert "MSDiff Diffusion" in out
    assert "Species 1" in out
    assert "Viscosity" not in out

    written = pd.read_csv(tmp_path / "res_out.csv", skipinitialspace=True)
    assert list(written.columns)[:2] == ["Species", "D_0 / 10^-12 m^2/s"]
    assert written["D_0 / 10^-12 m^2/s"].iloc[0] == pytest.approx(1.5)
    assert written["n_data"].iloc[0] == 91


def test_output_with_orthoboxy(
    results: pd.DataFrame, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    results["diffusion_coefficient_z"] = [1.2]
    results["delta_diffusion_coefficient_z"] = [0.05]
    results["eta"] = [0.9]
    results["delta_eta"] = [0.03]

    print_results_to_stdout(results)
    print_results_to_file(results, str(tmp_path / "res"))

    assert "Viscosity" in capsys.readouterr().out

    written = pd.read_csv(tmp_path / "res_out.csv", skipinitialspace=True)
    assert written["eta / 10^-3 Pa s"].iloc[0] == pytest.approx(0.9)
    assert written["D_z / 10^-12 m^2/s"].iloc[0] == pytest.approx(1.2)
