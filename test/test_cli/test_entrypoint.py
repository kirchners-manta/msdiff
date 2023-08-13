"""
Test for the command line entry point function
"""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from msdiff import console_entry_point


def test_entrypoint() -> None:
    example_file = Path(__file__).parent / "data" / "example.csv"
    with redirect_stdout(StringIO()):
        assert 0 == console_entry_point(
            f"-l 1234 -f {example_file} -o /dev/null".split()
        )
