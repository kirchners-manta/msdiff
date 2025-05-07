"""
Test command line options / arguments
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

import pytest

from msdiff import argparser, diffusion_coefficient


def test_defaults() -> None:
    """Test the default values of the command line arguments"""

    example_file = Path(__file__).parent / "data" / "example.csv"
    parser = argparser.parser()
    args = parser.parse_args(
        f"-f {example_file}".split()
    )  # add split because, the flags have to be given as arguments as well

    assert isinstance(args.avg, bool)
    assert args.avg == False

    assert isinstance(args.conductivity, bool)
    assert args.conductivity == False

    assert isinstance(args.hummer, tuple)
    assert len(args.hummer) == 3
    assert isinstance(args.hummer[0], float)
    assert isinstance(args.hummer[1], float)
    assert isinstance(args.hummer[2], float)
    assert args.hummer[0] == 350.00
    assert args.hummer[1] == 0.008277
    assert args.hummer[2] == 0.005039

    assert isinstance(args.from_travis, bool)
    assert args.from_travis == False

    assert isinstance(args.length, type(None))
    assert args.length == None

    assert isinstance(args.dimensions, int)
    assert args.dimensions == 3

    assert isinstance(args.output, str)
    assert args.output == "msdiff"

    assert isinstance(args.tolerance, float)
    assert args.tolerance == 0.1


def test_fail_type() -> None:
    """Test if the type of the arguments is correct"""

    example_file = Path(__file__).parent / "data" / "example.csv"

    parser = argparser.parser()

    with redirect_stderr(
        StringIO()
    ):  # this line is needed to not write the output to the console when testing
        with pytest.raises(SystemExit):
            parser.parse_args("-l abc".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --temp abc".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --tol abc".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --visco abc".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --d_visco abc".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --n abc".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {Path(__file__).parent / 'data'} ".split())
        with pytest.raises(SystemExit):
            parser.parse_args(
                f"-l 5000 -f {Path(__file__).parent / 'data' / 'yasdas'}".split()
            )


def test_fail_value() -> None:
    """Test if the value of the arguments is correct"""

    example_file = Path(__file__).parent / "data" / "example.csv"

    parser = argparser.parser()

    with redirect_stderr(
        StringIO()
    ):  # this line is needed to not write the output to the console when testing
        with pytest.raises(SystemExit):
            parser.parse_args("".split())
        with pytest.raises(SystemExit):
            parser.parse_args("-l 1".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --temp 123".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --tol 0.31".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --tol 0".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --visco -0.1".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --d_visco -0.1".split())
        with pytest.raises(SystemExit):
            parser.parse_args(f"-l 5000 -f {example_file} --n 0.2".split())
        with pytest.raises(SystemExit):
            parser.parse_args(
                f"-l 5000 -f {example_file} --hummer 50.0 1.0 1.0".split()
            )
        with pytest.raises(SystemExit):
            parser.parse_args(
                f"-l 5000 -f {example_file} --hummer 150.0 0.0 1.0".split()
            )
        with pytest.raises(SystemExit):
            parser.parse_args(
                f"-l 5000 -f {example_file} --hummer 150.0 1.0 -0.1".split()
            )


def test_no_travis_log() -> None:
    """Test if the Travis log file is present when option is called"""

    example_file = Path(__file__).parent / "data" / "example.csv"

    parser = argparser.parser()

    with redirect_stderr(StringIO()):
        with pytest.raises(FileNotFoundError):
            diffusion_coefficient(
                parser.parse_args(f"-l 5000 -f {example_file} --from-travis".split())
            )


def test_no_length() -> None:
    """Test if the box length is given"""

    example_file = Path(__file__).parent / "data" / "example.csv"

    parser = argparser.parser()

    with redirect_stderr(StringIO()):
        with pytest.raises(ValueError):
            diffusion_coefficient(parser.parse_args(f"-f {example_file}".split()))
