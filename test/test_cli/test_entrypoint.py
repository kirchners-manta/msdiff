"""
Test for the command line entry point function.
"""

from __future__ import annotations

import argparse
import copy
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from msdiff import console_entry_point
from msdiff.argparser import parser
from msdiff.cli import entrypoint as entrypoint_module
from msdiff.cli.entrypoint import resolve_defaults


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
    monkeypatch.setattr(entrypoint_module, "calculate_conductivity", fake_conductivity)

    console_entry_point(f"-l 1234 -f {example_file_msd}".split())
    console_entry_point(f"-f {example_file_cond} -c".split())

    assert observed == {
        "diffusion_species": 1,
        "diffusion_uncertainty": "none",
        "conductivity_species": 2,
        "conductivity_uncertainty": "var",
    }


@pytest.mark.parametrize(
    "options, species, uncertainty",
    [
        ("-l 1234", 1, "none"),  # diffusion defaults
        ("-c", 2, "var"),  # conductivity defaults
        ("-c -s 3 -u std", 3, "std"),  # user input wins over the defaults
        ("-l 1234 -s 2 -u var", 2, "var"),
    ],
)
def test_resolve_defaults(options: str, species: int, uncertainty: str) -> None:
    example_file = Path(__file__).parent / "data" / "example_msd.csv"
    args = parser().parse_args(f"-f {example_file} {options}".split())
    before = copy.deepcopy(vars(args))

    resolved = resolve_defaults(args)

    assert (resolved.species, resolved.uncertainty) == (species, uncertainty)
    # everything else is carried over, and the parsed arguments stay untouched
    assert vars(args) == before
    assert {k: v for k, v in vars(resolved).items() if k in before} == before
