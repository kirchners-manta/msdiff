"""
Test for the command line entry point function
"""

from __future__ import annotations

import os
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from msdiff import console_entry_point


def test_entrypoint() -> None:
    example_file_msd = Path(__file__).parent / "data" / "example_msd.csv"
    example_file_cond = Path(__file__).parent / "data" / "conductivity_test_data.csv"
    with redirect_stdout(StringIO()):
        assert 0 == console_entry_point(f"-l 1234 -f {example_file_msd}".split())
        os.system("rm msdiff_mols.csv msdiff_out.csv")
    with redirect_stdout(StringIO()):
        assert 0 == console_entry_point(f"-f {example_file_cond} -c".split())
        os.system("rm msdiff_post.csv msdiff_out.csv")
