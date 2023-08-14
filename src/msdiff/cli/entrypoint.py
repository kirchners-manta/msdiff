"""
Entrypoint for command line interface.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..argparser import parser
from ..diff_coeff import diffusion_coefficient


def console_entry_point(argv: Sequence[str] | None = None) -> int:
    # get arguments from command line and parse them
    args = parser().parse_args(argv)

    # hand over arguments to diffusion coefficient function
    diffusion_coefficient(args)

    return 0
