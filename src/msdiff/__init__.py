"""
MSDiff
======

Command-line tool to calculate diffusion coefficients and ionic conductivities
from (collective) mean square displacement (MSD) data of molecular dynamics
simulations. The input is a ``;``-separated csv file with time and MSD columns
(optionally with uncertainties), as written by the TRAVIS software.

Developed by Tom Frömbgen (Group of Prof. Dr. Barbara Kirchner, University of Bonn, Germany).
Published under the MIT license.
"""

from .__version__ import __version__
from .cli import console_entry_point
from .conductivity import calculate_conductivity
from .diffusion import (
    diffusion_coefficient,
    print_results_to_file,
    print_results_to_stdout,
)
from .functions import (
    calc_Hummer_correction,
    calc_orthoboxy_viscosity,
    calc_transport_numbers,
    find_linear_region,
    linear_fit,
    lmfit_linear_regression,
)
