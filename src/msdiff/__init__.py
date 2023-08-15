"""
MSDiff
======

This is a simple program to calculate the diffusion coefficient of molecules in a molecular dynamics simulation.
Required input comprises a data file containing the mean square displacement (MSD) as a function of time, with three columns: Time, MSD, and a third quantity which is irrelevant (but added to be suitable with output from the TRAVIS software).
This program is developed by Tom Frömbgen, (Group of Prof. Dr. Barbara Kirchner, University of Bonn, Germany).
It is published under the MIT license.
"""

from .__version__ import __version__
from .cli import console_entry_point
from .diff_coeff import diffusion_coefficient
from .functions import (
    calc_Hummer_correction,
    find_linear_region,
    get_diffusion_coefficient,
)
from .plotting import generate_simple_plot
