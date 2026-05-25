# MSDiff
---

![Python versions](https://img.shields.io/badge/python-3.11%20|%203.12-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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
Type `msdiff -h` to get a list of all available options:

Examples for the usage are given in the [examples](./examples) folder.

## Notes

* The [correction term by Hummer](https://pubs.acs.org/doi/10.1021/jp0477147) (to extrapolate to an infinite box size) is only valid for a cubic box. Other box shapes are not supported yet. [OrthoBoXY](https://doi.org/10.1021/acs.jpcb.3c04492) is supported, see description of the `--orthoboxy` option.


**Reference**

T. Frömbgen, P. Zaby, V. Alizadeh, J. L. F. Da Silva, B. Kirchner, T. C. Lourenço, Lessons learned on obtaining reliable dynamic properties for ionic liquids, *ChemPhysChem* (**2025**), e202401048.  DOI: [10.1002/cphc.202401048](https://doi.org/10.1002/cphc.202401048).

P. Zaby, J. Ingenmey, T. C. Lourenço, Y. Zhang, M. Brehm, E. J. Maginn, B. Kirchner, Lessons Learned on Obtaining Reliable Conductivity Estimates from Molecular Dynamics Simulations, *ChemRxiv* (**2026**), DOI [10.26434/chemrxiv.15002026/v3](https://doi.org/10.26434/chemrxiv.15002026/v3).
