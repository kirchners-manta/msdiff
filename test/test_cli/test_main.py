"""
Tests for running the package as a module.
"""

from __future__ import annotations

import subprocess
import sys

from msdiff import __version__


def test_python_dash_m_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "msdiff", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.strip() == f"msdiff {__version__}"
