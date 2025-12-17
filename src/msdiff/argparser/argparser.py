# Part of the AIMD setup tool

"""
Parser for command line options.
"""

#############################################

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

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
def action_not_less_than(min_value: float = 0.0) -> type[argparse.Action]:
    class CustomActionLessThan(argparse.Action):
        """
        Custom action for limiting possible input values. Raise error if value is smaller than min_value.
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,  # type: ignore
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


# def action_not_more_than(max_value: float = 0.0) -> type[argparse.Action]:
#     class CustomActionMoreThan(argparse.Action):
#         """
#         Custom action for limiting possible input values. Raise error if value is larger than max_value.
#         """

#         def __call__(
#             self,
#             p: argparse.ArgumentParser,
#             args: argparse.Namespace,
#             values: list[float | int] | float | int,  # type: ignore
#             option_string: str | None = None,
#         ) -> None:
#             if isinstance(values, (int, float)):
#                 values = [values]

#             if any(value > max_value for value in values):
#                 p.error(
#                     f"Option '{option_string}' takes only values smaller than {max_value}. {values} is not accepted."
#                 )

#             if len(values) == 1:
#                 values = values[0]

#             setattr(args, self.dest, values)

#     return CustomActionMoreThan


def action_in_range(
    min_value: float = 0.0, max_value: float = 1.0
) -> type[argparse.Action]:
    class CustomActionInRange(argparse.Action):
        """
        Custom action for limiting possible input values in a range. Raise error if value is not in range [min_value, max_value].
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float | int] | float | int,  # type: ignore
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


def action_check_hummer() -> type[argparse.Action]:
    class CustomActionHummer(argparse.Action):
        """
        Custom action for Hummer correction. Check if the correct number of arguments is given.
        """

        def __call__(
            self,
            p: argparse.ArgumentParser,
            args: argparse.Namespace,
            values: list[float],  # type: ignore
            option_string: str | None = None,
        ) -> None:

            # temperature has to be > 100
            if values[0] < 100.0:
                p.error(
                    f"Option '{option_string}' takes only values larger than 100. {values[0]} is not accepted."
                )
            # viscosity has to be > 0
            if len(values) == 1:
                values.append(0.008277)
            elif values[1] <= 0.0:
                p.error(
                    f"Option '{option_string}' takes only values larger than 0. {values[1]} is not accepted."
                )
            # delta_viscosity has to be >= 0
            if len(values) == 2:
                values.append(0.005039)
            elif values[2] < 0.0:
                p.error(
                    f"Option '{option_string}' takes only values larger than or equal to 0. {values[2]} is not accepted."
                )

            setattr(args, self.dest, values)

    return CustomActionHummer


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
def parser(name: str = "msdiff", **kwargs: Any) -> argparse.ArgumentParser:
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
        "-f",
        "--file",
        type=is_file,
        metavar="MSD_FILE",
        dest="file",
        required=True,
        help="R|File containing the mean square displacement in csv format",
    )
    p.add_argument(
        "-a",
        "--avg",
        action="store_true",
        dest="avg",
        help="R|The input file contains the average values and the standard deviation.",
        default=False,
    )
    p.add_argument(
        "-c",
        "--conductivity",
        action="store_true",
        dest="conductivity",
        help="R|Calculate the conductivity instead of the diffusion coefficient.",
        default=False,
    )
    p.add_argument(
        "--from-travis",
        action="store_true",
        dest="from_travis",
        help="R|If the input file is an MSD from TRAVIS in the lmp format,\nthe box length can be read from the 'travis.log' file.",
        default=False,
    )
    p.add_argument(
        "--hummer",
        action=action_check_hummer(),
        dest="hummer",
        default=[
            350.0,
            0.008277,
            0.005039,
        ],  # eta and d_eta calculated from equation in https://doi.org/10.1021/jp044626d
        nargs="+",
        type=float,
        help="R|Use the Hummer correction for the diffusion coefficient.\nThe values are given in the format 'Temperature, Viscosity, delta_Viscosity' (comma separated).\nThe temperature is in K, the viscosity in kg/(m*s) and the d_Viscosity in kg/(m*s).",
    )
    p.add_argument(
        "-l",
        type=float,
        metavar="L",
        dest="length",
        help="R|Length of the cubic box in pm. Provide lx if the box is cubic or lx, ly and lz (space separated) if the box is rectangular.",
        action=action_not_less_than(500.0),
        nargs="+",
        default=None,
    )
    p.add_argument(
        "--dim",
        type=int,
        metavar="N",
        dest="dimensions",
        help="R|Number of dimensions, the diffusion coefficient should be calculated for.",
        default=3,
        choices=[1, 2, 3],
    )
    p.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="OUTPUT",
        help="R|Output file name, without file extension. Default is 'msdiff', which will create 'msdiff_out.csv'.",
        default="msdiff",
    )
    p.add_argument(
        "--orthoboxy",
        dest="orthoboxy",
        type=is_file,
        metavar="MSD_FILE",
        help="R|If the box is tetragonal with Lz/Lx = Lz/Ly = 2.7933596497, the Hummer correction is 0.\nThe file read in with the -f option is assumed to be the MSD in x and y directions.\nThe dimensionality of the system will be set to 2.\nThe file read in with this option is assumed to be the MSD in z direction.\nThe viscosity will be calculated from the OrthoBoXY formula.\nThat requires the temperature, which can be given with the --hummer option (only the first argument is used).",
        default=None,
    )
    p.add_argument(
        "--tol",
        type=float,
        dest="tolerance",
        help="R|Tolerance for identifying the linear region.",
        default=0.10,
        action=action_in_range(0.001, 0.3),
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"{name} {__version__}",
        help="R|Show version and exit.",
    )
    return p
