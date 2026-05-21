"""
Entrypoint for command line interface.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..argparser import parser
from ..conductivity import conductivity
from ..diffusion import diffusion_coefficient


def console_entry_point(argv: Sequence[str] | None = None) -> int:
    # get arguments from command line and parse them
    args = parser().parse_args(argv)
    
    # if the user did not specify the number of species, determine the default based on whether conductivity or diffusion coefficient is being calculated
    if not hasattr(args, "species"):
        args.species = 2 if args.conductivity else 1

    if not args.conductivity:
        # hand over arguments to diffusion coefficient function
        diffusion_coefficient(args)
    else:
        # hand over arguments to conductivity function
        conductivity(args)

    return 0
