"""
Entrypoint for command line interface.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..argparser import parser
from ..diffusion import diffusion_coefficient
from ..conductivity import conductivity


def console_entry_point(argv: Sequence[str] | None = None) -> int:
    # get arguments from command line and parse them
    args = parser().parse_args(argv)

    if not args.conductivity:
        # hand over arguments to diffusion coefficient function
        diffusion_coefficient(args)
    else:
        # hand over arguments to conductivity function
        conductivity(args)

    return 0
