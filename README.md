# MSDiff
---

![Python versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
![Tests](https://github.com/tomfroembgen/python-project/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/tomfroembgen/python-project/branch/main/graph/badge.svg?token=UEKDZY459S)](https://codecov.io/gh/tomfroembgen/python-project)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tomfroembgen/python-project/main.svg)](https://results.pre-commit.ci/latest/github/tomfroembgen/python-project/main)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository offers a tool to calculate the diffusion coefficient based on molecular dynamics simulations.
The program takes the output of an MSD calculation by TRAVIS and calculates the diffusion coefficient based on the slope of the mean square displacement.
It is primarily written for the [group of Barbara Kirchner](https://www.chemie.uni-bonn.de/kirchner/de/startseite) at the University of Bonn and published under the [MIT license](./LICENSE).

## Installation

The tool can be installed using `pip`:

```bash
git clone git@github.com:tomfroembgen/msdiff.git
cd msdiff
pip install .
```

## Usage

The program is designed as a command line tool. 
It takes the following inputs:
```
usage: msdiff [-h] -l LENGTH -f data_file [-o OUTPUT] [-p] [-t TEMPERATURE] [--tol TOLERANCE] [-v VISCOSITY]
```
* `-l` or `--length` takes the length of the cubic box in pm.
* `-f` or `--file` takes the file containing the mean square displacement in csv format with time (in ps) in the first column and the MSD (in pm^2) in the second column. A third column can be given and will be ignored (usually the derivative in a TRAVIS MSD calculation).
* `-o` or `--output` takes the output file name. The default is `msdiff_out.csv`.
* `-p` or `--plot` generates a visualization of the MSD in log-log representation (`.pdf`) and shows the linear regime. The default is `False`.
* `-t` or `--temperature` takes the temperature in K. The default is `353.15`.
* `--tol` or `--tolerance` takes the tolerance for identifying the linear region. The default is `0.05`.
* `-v` or `--viscosity` takes the dynamic viscosity of the system in kg/(m*s). The default is `0.00787` (value for [EMIM][NTF2] at 353.15 K).

Examples for the usage are given in the [examples](./examples) folder.

