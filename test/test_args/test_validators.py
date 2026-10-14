"""
Tests for the argument validators and custom argparse actions.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from msdiff import argparser

DATA_FILE = Path(__file__).parent / "data" / "example.csv"


def test_is_file(tmp_path: Path) -> None:
    assert argparser.argparser.is_file(str(DATA_FILE)) == str(DATA_FILE)

    with pytest.raises(argparse.ArgumentTypeError, match="Is a directory"):
        argparser.argparser.is_file(str(tmp_path))
    with pytest.raises(argparse.ArgumentTypeError, match="No such file"):
        argparser.argparser.is_file(str(tmp_path / "missing.csv"))


def test_is_dir(tmp_path: Path) -> None:
    assert argparser.argparser.is_dir(str(tmp_path)) == str(tmp_path)

    with pytest.raises(argparse.ArgumentTypeError, match="Is not a directory"):
        argparser.argparser.is_dir(str(DATA_FILE))
    with pytest.raises(argparse.ArgumentTypeError, match="No such file or directory"):
        argparser.argparser.is_dir(str(tmp_path / "missing"))


@pytest.mark.parametrize(
    "options, dest, expected",
    [
        ("-l 1234", "length", 1234.0),
        ("-l 1234 1500", "length", [1234.0, 1500.0]),
        ("-s 3", "species", 3),
        ("--tol 0.05", "tolerance", 0.05),
        ("--incr 0.1", "linreg_incr", 0.1),
    ],
)
def test_actions_accept_valid_values(options: str, dest: str, expected: object) -> None:
    args = argparser.parser().parse_args(f"-f {DATA_FILE} {options}".split())

    # a single value is unpacked from its list, several values stay a list
    assert getattr(args, dest) == expected


@pytest.mark.parametrize(
    "options, message",
    [
        ("-l 100", "takes only values larger than 500.0"),
        ("-s 0", "takes only values larger than 1"),
        ("--tol 0.5", "takes only values between 0.001 and 0.3"),
        ("--tol 0.0001", "takes only values between 0.001 and 0.3"),
        ("--incr 0.9", "takes only values between 0.001 and 0.5"),
        ("--slice 0", "takes only values larger than 1"),
        ("--hummer -5", "larger than 0 K"),
        ("--hummer 300 0", "larger than 0 kg/(m*s)"),
        ("--hummer 300 0.01 -0.1", ">= 0 kg/(m*s)"),
    ],
)
def test_actions_reject_invalid_values(
    options: str, message: str, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        argparser.parser().parse_args(f"-f {DATA_FILE} {options}".split())

    assert message in capsys.readouterr().err


@pytest.mark.parametrize(
    "options, expected",
    [
        ("--hummer 300", [300.0, 0, 0]),
        ("--hummer 300 0.01", [300.0, 0.01, 0]),
        ("--hummer 300 0.01 0.001", [300.0, 0.01, 0.001]),
    ],
)
def test_hummer_action_pads_missing_values(options: str, expected: list[float]) -> None:
    args = argparser.parser().parse_args(f"-f {DATA_FILE} {options}".split())

    assert args.hummer == expected


def test_version_and_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        argparser.parser(name="msdiff").parse_args(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith("msdiff ")

    with pytest.raises(SystemExit) as exc:
        argparser.parser().parse_args(["-h"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    # the custom formatter appends defaults and keeps the explicit line breaks
    assert "- default: msdiff" in out
    assert "'var' is variance" in out
