""" 
Test the input reader for MSDiff
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from msdiff import process_input


def test_1_columns() -> None:
    with pytest.raises(ValueError):
        process_input(Path(__file__).parent / "data" / "1cols.csv")


def test_2_columns() -> None:
    data, nmols = process_input(Path(__file__).parent / "data" / "2cols.csv")
    assert nmols == 1
    assert len(data.columns) == 2
    assert data.columns[0] == "time"
    assert data.columns[1] == "msd_1"


def test_3_columns() -> None:
    data, nmols = process_input(Path(__file__).parent / "data" / "3cols.csv")
    assert nmols == 1
    assert len(data.columns) == 2
    assert data.columns[0] == "time"
    assert data.columns[1] == "msd_1"


def test_many_columns() -> None:
    data, nmols = process_input(Path(__file__).parent / "data" / "manycols.csv")
    assert nmols == 5
    assert len(data.columns) == 7
    assert data.columns[0] == "time"
    assert data.columns[1] == "msd_total"
    assert data.columns[-1] == f"msd_{nmols}"
