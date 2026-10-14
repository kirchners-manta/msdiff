"""
Tests for the box length handling of the diffusion coefficient calculation.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from msdiff.diffusion.diff_coeff import read_box_length_from_travis, resolve_box_length

TRAVIS_LOG = "\n".join(
    [
        "prefix",
        "Found cell geometry data in trajectory file",
        "ignored",
        "A B 111 C D E 222 F G H 333",
    ]
)


@pytest.mark.parametrize(
    "length, expected",
    [
        (1234.0, [1234.0, 1234.0, 1234.0]),  # single value: cubic box
        ([1000.0, 1500.0], [1000.0, 1000.0, 1500.0]),  # lx lz, with ly = lx
        ([1000.0, 1200.0, 1500.0], [1000.0, 1200.0, 1500.0]),
    ],
)
def test_resolve_box_length_shapes(
    length: float | list[float], expected: list[float]
) -> None:
    given = list(length) if isinstance(length, list) else length

    assert resolve_box_length(length, False, "msd.csv") == expected
    # the input is not modified
    assert length == given


def test_resolve_box_length_without_length_warns(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert resolve_box_length(None, False, "msd.csv") == [0.0, 0.0, 0.0]
    assert "No box length given" in capsys.readouterr().out


def test_resolve_box_length_rejects_too_many_values() -> None:
    with pytest.raises(ValueError, match="Too many"):
        resolve_box_length([1000.0] * 4, False, "msd.csv")


def test_resolve_box_length_from_travis_ignores_length(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "travis.log").write_text(TRAVIS_LOG, encoding="utf8")

    result = resolve_box_length(1234.0, True, tmp_path / "msd.csv")

    assert result == [111.0, 222.0, 333.0]
    assert "read from travis.log" in capsys.readouterr().out


def test_read_box_length_from_travis(tmp_path: Path) -> None:
    log = tmp_path / "travis.log"
    log.write_text(TRAVIS_LOG, encoding="utf8")

    assert read_box_length_from_travis(log) == [111.0, 222.0, 333.0]


def test_read_box_length_from_travis_errors(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="travis.log not found"):
        read_box_length_from_travis(tmp_path / "travis.log")

    log = tmp_path / "travis.log"
    log.write_text("no cell information\n", encoding="utf8")
    with pytest.raises(ValueError, match="No cell geometry"):
        read_box_length_from_travis(log)
