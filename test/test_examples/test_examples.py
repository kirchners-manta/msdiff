"""
Regression tests: re-run every example from ``examples/`` and compare to the
committed reference output (``msdiff_out.csv`` / ``msdiff_tp.csv``).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from msdiff import console_entry_point

EXAMPLES = Path(__file__).parents[2] / "examples"

# (example directory, command line options, number of reference files to compare)
CASES = {
    "ntf2": (
        "diffusion/ntf2",
        "-f msd_ntf2.csv -l 6134.48 --hummer 350.0 0.008277 0.005039",
        ["out"],
    ),
    "std": (
        "diffusion/standard_deviation",
        "-f msd_c2c1im_std.csv -u std",
        ["out"],
    ),
    "orthoboxy": (
        "diffusion/orthoboxy",
        "-f msd_H2O_#2_XY.csv -z msd_H2O_#2_Z.csv --from-travis --hummer 330",
        ["out"],
    ),
    "cond_2comp": (
        "conductivity/2_comp",
        "-f conductivity_test_data.csv -c -u none",
        ["out", "tp"],
    ),
    "cond_3comp": (
        "conductivity/3_comp",
        "-f conduct_3comp.csv -c -u var -s 3",
        ["out", "tp"],
    ),
}


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, skipinitialspace=True)


@pytest.mark.parametrize("case", CASES)
def test_example_reproduces_reference_output(
    case: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    directory, options, suffixes = CASES[case]
    folder = EXAMPLES / directory

    # input paths are made absolute (travis.log is looked up next to the input),
    # the output goes to a temporary directory to keep the examples untouched
    argv = []
    for token in options.split():
        argv.append(str(folder / token) if token.endswith(".csv") else token)
    argv += ["-o", str(tmp_path / "msdiff")]

    assert console_entry_point(argv) == 0
    capsys.readouterr()

    for suffix in suffixes:
        new = _read(tmp_path / f"msdiff_{suffix}.csv")
        reference = _read(folder / f"msdiff_{suffix}.csv")
        pd.testing.assert_frame_equal(new, reference, rtol=1e-4, atol=1e-6)
