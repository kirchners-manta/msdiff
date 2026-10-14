"""
Entrypoint for command line interface.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from ..argparser import parser
from ..conductivity import calculate_conductivity
from ..diffusion import diffusion_coefficient


def resolve_defaults(args: argparse.Namespace) -> argparse.Namespace:
    """Fill in the defaults that depend on the type of calculation.

    ``--species`` and ``--uncertainty`` are not given a fixed default by the
    parser, because it depends on whether the conductivity (``-c``) or the
    diffusion coefficient is calculated.

    Parameters
    ----------
    args : argparse.Namespace
        The parsed command line arguments. Is not modified.

    Returns
    -------
    argparse.Namespace
        A new namespace with ``species`` and ``uncertainty`` set. Values given
        by the user take precedence over the defaults.
    """
    defaults = {
        "species": 2 if args.conductivity else 1,
        "uncertainty": "var" if args.conductivity else "none",
    }
    # options not given on the command line are absent from ``vars(args)``
    return argparse.Namespace(**{**defaults, **vars(args)})


def console_entry_point(argv: Sequence[str] | None = None) -> int:
    """Parse the command line and run the diffusion or conductivity workflow.

    Parameters
    ----------
    argv : Sequence[str] | None
        Command line arguments (without the program name). If ``None``,
        ``sys.argv[1:]`` is used.

    Returns
    -------
    int
        Exit code of the program (0 on success).
    """
    # get arguments from command line and parse them
    args = resolve_defaults(parser().parse_args(argv))

    if not args.conductivity:
        # hand over arguments to diffusion coefficient function
        diffusion_coefficient(args)
    else:
        # hand over arguments to conductivity function
        calculate_conductivity(args)

    return 0
