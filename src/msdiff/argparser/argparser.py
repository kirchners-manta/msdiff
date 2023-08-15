# Part of the AIMD setup tool

"""
Parser for command line options.
"""

#############################################

from __future__ import annotations

import argparse
from pathlib import Path

from .. import __version__


# file and directory checks
def is_file(path: str | Path) -> str | Path:
    p = Path(path)

    if p.is_dir():
        raise argparse.ArgumentTypeError(
            f"Cannot open '{path}': Is a directory.",
        )

    if p.is_file() is False:
        raise argparse.ArgumentTypeError(
            f"Cannot open '{path}': No such file.",
        )

    return path


def is_dir(path: str | Path) -> str | Path:
    p = Path(path)

    if p.is_file():
        raise argparse.ArgumentTypeError(
            f"Cannot open '{path}': Is not a directory.",
        )

    if p.is_dir() is False:
        raise argparse.ArgumentTypeError(
            f"Cannot open '{path}': No such file or directory.",
        )

    return path


# custom actions
def action_not_less_than(min_value: float = 0.0):
    class CustomActionLessThan(argparse.Action):
        """
        Custom action for limiting possible input values. Raise error if value is smaller than min_value.
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,
            option_string: str | None = None,
        ) -> None:
            if isinstance(values, (int, float)):
                values = [values]

            if any(value < min_value for value in values):
                p.error(
                    f"Option '{option_string}' takes only values larger than {min_value}. {values} is not accepted."
                )

            if len(values) == 1:
                values = values[0]

            setattr(args, self.dest, values)

    return CustomActionLessThan


def action_not_more_than(max_value: float = 0.0):
    class CustomActionMoreThan(argparse.Action):
        """
        Custom action for limiting possible input values. Raise error if value is larger than max_value.
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,
            option_string: str | None = None,
        ) -> None:
            if isinstance(values, (int, float)):
                values = [values]

            if any(value > max_value for value in values):
                p.error(
                    f"Option '{option_string}' takes only values smaller than {max_value}. {values} is not accepted."
                )

            if len(values) == 1:
                values = values[0]

            setattr(args, self.dest, values)

    return CustomActionMoreThan


def action_in_range(min_value: float = 0.0, max_value: float = 1.0):
    class CustomActionInRange(argparse.Action):
        """
        Custom action for limiting possible input values in a range. Raise error if value is not in range [min_value, max_value].
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,
            option_string: str | None = None,
        ) -> None:
            if isinstance(values, (int, float)):
                values = [values]

            if any(value < min_value or value > max_value for value in values):
                p.error(
                    f"Option '{option_string}' takes only values between {min_value} and {max_value}. {values} is not accepted."
                )

            if len(values) == 1:
                values = values[0]

            setattr(args, self.dest, values)

    return CustomActionInRange


# custom formatter
class Formatter(argparse.HelpFormatter):
    """
    Custom format for help message.
    """

    def _get_help_string(self, action: argparse.Action) -> str | None:
        """
        Append default value and type of action to help string.

        Parameters
        ----------
        action : argparse.Action
            Command line option.

        Returns
        -------
        str | None
            Help string.
        """
        helper = action.help
        if helper is not None and "%(default)" not in helper:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]

                if action.option_strings or action.nargs in defaulting_nargs:
                    helper += "\n - default: %(default)s"
                # uncomment if type is needed to be shown in help message
                # if action.type:
                #     helper += "\n - type: %(type)s"

        return helper

    def _split_lines(self, text: str, width: int) -> list[str]:
        """
        Re-implementation of `RawTextHelpFormatter._split_lines` that includes
        line breaks for strings starting with 'R|'.

        Parameters
        ----------
        text : str
            Help message.
        width : int
            Text width.

        Returns
        -------
        list[str]
            Split text.
        """
        if text.startswith("R|"):
            return text[2:].splitlines()

        # pylint: disable=protected-access
        return argparse.HelpFormatter._split_lines(self, text, width)


# custom parser
def parser(name: str = "msdiff", **kwargs) -> argparse.ArgumentParser:
    """
    Parses the command line arguments.

    Returns
    -------
    argparse.ArgumentParser
        Container for command line arguments.
    """

    p = argparse.ArgumentParser(
        prog="msdiff",
        description="Program to calculate the diffusion coefficient from a TRAVIS MSD output.",
        epilog="Written for the Kirchner group by Tom Frömbgen.",
        formatter_class=lambda prog: Formatter(prog, max_help_position=60),
        add_help=False,
        **kwargs,
    )
    p.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="R|Show this help message and exit.",
    )
    p.add_argument(
        "-l",
        "--len",
        type=float,
        metavar="LENGTH",
        dest="length",
        help="R|Length of the cubic box in pm.",
        action=action_not_less_than(500.0),
        required=True,
    )
    p.add_argument(
        "-f",
        "--file",
        type=is_file,
        metavar="MSD_FILE",
        dest="file",
        required=True,
        help="R|File containing the mean square displacement in csv format",
    )
    p.add_argument(
        "--d_visco",
        type=float,
        metavar="DELTA_VISCOSITY",
        dest="delta_viscosity",
        help="R|(Experimental) error of the dynamic viscosity of the system in kg/(m*s)",
        default=0.0,
        action=action_not_less_than(0.0),
    )
    p.add_argument(
        "--from-travis",
        action="store_true",
        dest="from_travis",
        help="R|If the input file is an MSD from TRAVIS in the lmp format, the box length can be read from the 'travis.log' file.",
        default=False,
    )
    p.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="OUTPUT",
        help="R|Output file name.",
        default="msdiff_out.csv",
    )
    p.add_argument(
        "-p",
        "--plot",
        action="store_true",
        help="R|Plot the MSD and the linear fit.",
        default=False,
    )
    p.add_argument(
        "-t",
        "--temp",
        type=float,
        metavar="TEMPERATURE",
        dest="temperature",
        help="R|Temperature in K",
        default=353.15,
        action=action_not_less_than(200.0),
    )
    p.add_argument(
        "--tol",
        type=float,
        dest="tolerance",
        help="R|Tolerance for identifying the linear region.",
        default=0.05,
        action=action_in_range(0.001, 0.3),
    )
    p.add_argument(
        "-v",
        "--visco",
        dest="viscosity",
        type=float,
        metavar="VISCOSITY",
        help="R|Dynamic viscosity of the system in kg/(m*s)",
        default=0.00787,  # 0.00787 for [EMIM][NTf2] / 0.00958 for [EMIM][BF4]
        action=action_not_less_than(0.0),
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"{name} {__version__}",
        help="R|Show version and exit.",
    )
    return p
