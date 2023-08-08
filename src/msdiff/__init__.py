"""
MSDiff
======

This is a simple program to calculate the diffusion coefficient of molecules in a molecular dynamics simulation.
An MSD calculation by TRAVIS is required as input.
This program is developed by Tom Frömbgen, (Group of Prof. Dr. Barbara Kirchner, University of Bonn, Germany) and maily designed for the use in this group.
It is published under the MIT license.
"""

from .__version__ import __version__
from .cli import console_entry_point
