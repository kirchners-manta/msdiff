"""
Test for the command line entry point function.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from msdiff import console_entry_point
from msdiff.cli import entrypoint as entrypoint_module


def test_entrypoint(tmp_path: Path) -> None:
    example_file_msd = Path(__file__).parent / "data" / "example_msd.csv"
    example_file_cond = Path(__file__).parent / "data" / "conductivity_test_data.csv"
    testout = tmp_path / "test"

    with redirect_stdout(StringIO()):
        assert 0 == console_entry_point(
            f"-l 1234 -f {example_file_msd} -o {testout}".split()
        )

    assert (tmp_path / "test_out.csv").is_file()

    with redirect_stdout(StringIO()):
        assert 0 == console_entry_point(
            f"-f {example_file_cond} -o {testout} -c -u none".split()
        )

    assert (tmp_path / "test_out.csv").is_file()
    assert (tmp_path / "test_tp.csv").is_file()


def test_entrypoint_infers_default_species(monkeypatch: MonkeyPatch) -> None:
    example_file_msd = Path(__file__).parent / "data" / "example_msd.csv"
    example_file_cond = Path(__file__).parent / "data" / "conductivity_test_data.csv"
    observed = {}

    def fake_diffusion(args: argparse.Namespace) -> None:
        observed["diffusion_species"] = args.species
        observed["diffusion_uncertainty"] = args.uncertainty

    def fake_conductivity(args: argparse.Namespace) -> None:
        observed["conductivity_species"] = args.species
        observed["conductivity_uncertainty"] = args.uncertainty

    monkeypatch.setattr(entrypoint_module, "diffusion_coefficient", fake_diffusion)
    monkeypatch.setattr(entrypoint_module, "conductivity", fake_conductivity)

    console_entry_point(f"-l 1234 -f {example_file_msd}".split())
    console_entry_point(f"-f {example_file_cond} -c".split())

    assert observed == {
        "diffusion_species": 1,
        "diffusion_uncertainty": "none",
        "conductivity_species": 2,
        "conductivity_uncertainty": "var",
    }
