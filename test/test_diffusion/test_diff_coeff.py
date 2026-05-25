"""
Tests for diffusion coefficient orchestration.
"""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from _pytest.monkeypatch import MonkeyPatch

from msdiff import argparser
from msdiff.diffusion.diff_coeff import diffusion_coefficient


def test_diffusion_coefficient_normalizes_cubic_length(
    monkeypatch: MonkeyPatch,
) -> None:
    example_file = Path(__file__).parents[1] / "test_args" / "data" / "example.csv"
    parser = argparser.parser()
    args = parser.parse_args(f"-f {example_file} -l 1234".split())
    args.species = 1
    args.uncertainty = "none"
    observed: dict[str, Any] = {}

    msd_data = pd.DataFrame(
        {
            "time": [0.0, 1.0, 2.0, 3.0, 4.0],
            "msd_1_self": [0.0, 2.0, 4.0, 6.0, 8.0],
            "msd_1_self_std": [0.0] * 5,
        }
    )

    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.read_input_diffusion",
        lambda *args, **kwargs: msd_data,
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.find_linear_region",
        lambda *args, **kwargs: [1, 4],
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.linear_fit",
        lambda *args, **kwargs: [6.0, 0.6, 0.99, 4],
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.calc_Hummer_correction",
        lambda *args, **kwargs: [1.5, 0.2],
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.print_results_to_stdout",
        lambda results: observed.setdefault("results", results.copy()),
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.print_results_to_file",
        lambda results, output: observed.setdefault("output", output),
    )

    with redirect_stdout(StringIO()):
        assert diffusion_coefficient(args) == 0

    assert args.length == [1234.0, 1234.0, 1234.0]
    assert args.cubic == True
    assert observed["results"]["lx"].iloc[0] == 1234.0
    assert observed["results"]["diffusion_coefficient"].iloc[0] == 1.0


def test_diffusion_coefficient_reads_box_lengths_from_travis_log(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    data_file = tmp_path / "msd.csv"
    data_file.write_text("# header\n0;0;0\n1;1;0\n2;2;0\n", encoding="utf8")
    (tmp_path / "travis.log").write_text(
        "\n".join(
            [
                "prefix",
                "Found cell geometry data in trajectory file",
                "ignored",
                "A B 111 C D E 222 F G H 333",
            ]
        ),
        encoding="utf8",
    )

    parser = argparser.parser()
    args = parser.parse_args(f"-f {data_file} --from-travis".split())
    args.species = 1
    args.uncertainty = "none"

    msd_data = pd.DataFrame(
        {
            "time": [0.0, 1.0, 2.0, 3.0, 4.0],
            "msd_1_self": [0.0, 2.0, 4.0, 6.0, 8.0],
            "msd_1_self_std": [0.0] * 5,
        }
    )

    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.read_input_diffusion",
        lambda *args, **kwargs: msd_data,
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.find_linear_region",
        lambda *args, **kwargs: [1, 4],
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.linear_fit",
        lambda *args, **kwargs: [6.0, 0.6, 0.99, 4],
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.calc_Hummer_correction",
        lambda *args, **kwargs: [0.0, 0.0],
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.print_results_to_stdout",
        lambda results: None,
    )
    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.print_results_to_file",
        lambda results, output: None,
    )

    with redirect_stdout(StringIO()):
        diffusion_coefficient(args)

    assert args.length == [111.0, 222.0, 333.0]
    assert args.cubic == False


def test_diffusion_coefficient_rejects_cubic_orthoboxy(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    xy_file = tmp_path / "xy.csv"
    z_file = tmp_path / "z.csv"
    xy_file.write_text("# header\n0;0;0\n1;1;0\n", encoding="utf8")
    z_file.write_text("# header\n0;0;0\n1;1;0\n", encoding="utf8")

    parser = argparser.parser()
    args = parser.parse_args(f"-f {xy_file} -l 1234 --orthoboxy {z_file}".split())
    args.species = 1
    args.uncertainty = "none"

    monkeypatch.setattr(
        "msdiff.diffusion.diff_coeff.print_program_header",
        lambda: None,
    )

    with pytest.raises(ValueError, match="Cubic box does not make sense for OrthoBoXY"):
        diffusion_coefficient(args)
