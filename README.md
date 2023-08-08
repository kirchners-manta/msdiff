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

