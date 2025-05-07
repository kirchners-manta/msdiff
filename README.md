# MSDiff
---

![Python versions](https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository offers a tool to calculate the diffusion coefficient based on molecular dynamics simulations.
The program takes the output of an MSD calculation by TRAVIS (or any other program, as long as the format fits, see below) and calculates the diffusion coefficient and the ionic conductivity based on the slope of the mean square displacement.
It is primarily designed for the [group of Barbara Kirchner](https://www.chemie.uni-bonn.de/kirchner/de/startseite) at the University of Bonn but open to everyone and published under the [MIT license](./LICENSE).

## Installation

The tool can be installed using `pip`:

```bash
git clone git@github.com:kirchners-manta/msdiff.git
cd msdiff
pip install .
```

## Usage

The program is designed as a command line tool.
Type `msdiff -h` to get a list of all available options:
```
  -h, --help                     Show this help message and exit.
  -f MSD_FILE, --file MSD_FILE   File containing the mean square displacement in csv format
                                  - default: None
  -a, --avg                      The input file contains the average values and the standard deviation.
                                  - default: False
  -c, --conductivity             Calculate the conductivity instead of the diffusion coefficient.
                                  - default: False
  --from-travis                  If the input file is an MSD from TRAVIS in the lmp format,
                                 the box length can be read from the 'travis.log' file.
                                  - default: False
  --hummer HUMMER HUMMER HUMMER  Use the Hummer correction for the diffusion coefficient.
                                 The values are given in the format 'Temperature, Viscosity, delta_Viscosity' (comma separated).
                                 The temperature is in K, the viscosity in kg/(m*s) and the d_Viscosity in kg/(m*s).
                                  - default: (350.0, 0.008277, 0.005039)
  -l L [L ...]                   Length of the cubic box in pm. Provide lx if the box is cubic or lx, ly and lz (space separated) if the box is rectangular.
                                  - default: None
  --dim N                        Number of dimensions, the diffusion coefficient should be calculated for.
                                  - default: 3
  -o OUTPUT, --output OUTPUT     Output file name, without file extension. Default is 'msdiff', which will create 'msdiff_out.csv'.
                                  - default: msdiff
  --orthoboxy MSD_FILE           If the box is tetragonal with Lz/Lx = Lz/Ly = 2.7933596497, the Hummer correction is 0.
                                 The file read in with the -f option is assumed to be the MSD in x and y directions.
                                 The dimensionality of the system will be set to 2.
                                 The file read in with this option is assumed to be the MSD in z direction.
                                 The viscosity will be calculated from the OrthoBoXY formula.
                                 That requires the temperature, which can be given with the --hummer option (only the first argument is used).
                                  - default: None
  --tol TOLERANCE                Tolerance for identifying the linear region.
                                  - default: 0.1
  --version                      Show version and exit.
```

Examples for the usage are given in the [examples](./examples) folder.

## Notes

* Currently, the program only supports the MSD or conductivity output format of TRAVIS.
* The [correction term by Hummer](https://pubs.acs.org/doi/10.1021/jp0477147) (to extrapolate to an infinite box size) is only valid for a cubic box. Other box shapes are not supported yet. [OrthoBoXY](https://doi.org/10.1021/acs.jpcb.3c04492) is supported, see description of the `--orthoboxy` option.
