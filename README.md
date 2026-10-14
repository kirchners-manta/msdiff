# MSDiff
---

[![CI](https://github.com/kirchners-manta/msdiff/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/kirchners-manta/msdiff/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/kirchners-manta/msdiff/branch/main/graph/badge.svg)](https://codecov.io/gh/kirchners-manta/msdiff)
[![Paper I](https://img.shields.io/badge/Paper%20I-ChemPhysChem%202025-informational.svg)](https://doi.org/10.1002/cphc.202401048)
[![Paper II](https://img.shields.io/badge/Paper%20II-ChemPhysChem%202026-informational.svg)](https://doi.org/10.1002/cphc.70477)
![Python versions](https://img.shields.io/badge/python-3.12%20|%203.13%20|%203.14-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-2a6db2.svg)](https://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

This repository offers a command-line software tool to calculate the diffusion coefficient and ionic conductivity from self and collective mean square displacement (MSD) data from molecular dynamics simulations.
It is primarily designed to operate with outputs from the TRAVIS software, but the input format is not too strict, and it can be used with MSD data from other sources as well.

## Installation

The tool can be installed using `pip`:

```bash
git clone git@github.com:kirchners-manta/msdiff.git
cd msdiff
pip install .
```

## Usage

The program is designed as a command line tool.
Type `msdiff -h` to get a list of all available options.
Examples for the usage are given in the [examples](./examples) folder.

## Development

```bash
conda env create -f environment.yaml
conda activate msdiff
pip install -e ".[dev]"
pre-commit install
coverage run -m pytest && coverage report -m
```

Python >= 3.12 is required; CI tests 3.12, 3.13, and 3.14.

## Notes

* The [correction term by Hummer](https://pubs.acs.org/doi/10.1021/jp0477147) (to extrapolate to an infinite box size) is only valid for a cubic box. Other box shapes are not supported yet. [OrthoBoXY](https://doi.org/10.1021/acs.jpcb.3c04492) is supported, see description of the `--orthoboxy` option.


**Reference**

T. Frömbgen, P. Zaby, V. Alizadeh, J. L. F. Da Silva, B. Kirchner, T. C. Lourenço, Lessons learned on obtaining reliable dynamic properties for ionic liquids, *ChemPhysChem* (**2025**), e202401048.  DOI: [10.1002/cphc.202401048](https://doi.org/10.1002/cphc.202401048).

P. Zaby, J. Ingenmey, T. C. Lourenço, Y. Zhang, J. L. F. Da Silva, M. Brehm, E. J. Maginn, B. Kirchner, Lessons Learned on Obtaining Reliable Conductivity Estimates From Molecular Dynamics Simulations, *ChemPhysChem* (**2026**), 27, e70477.  DOI: [10.1002/cphc.70477](https://doi.org/10.1002/cphc.70477).
