# Examples for MSDiff

## General information

Upon calling `msdiff -h`, a list of all available options is shown, which are explained in the help message.
* `-f/--file` is used to specify the input file, which should be a CSV file with `;` as delimiter containing diffusion or conductivity data.
The expected format depends on the type of calculation and on `-u/--uncertainty`:
  * For diffusion with `-u none`:
    * `time`, `MSD_species1`, `MSD_species2`, ...
    * In total, there should be `1 + n_species` columns.
  * For diffusion with `-u std` or `-u var`:
    * `time`, `MSD_species1`, `uncertainty_species1`, `MSD_species2`, `uncertainty_species2`, ...
    * In total, there should be `1 + 2 * n_species` columns.
  * For conductivity with `-u none`:
    * `time`,
    * `MSD_self_species1`, `MSD_self_species2`, ...,
    * `MSD_cross_species1`, `MSD_cross_species2`, ...,
    * `Twobody_species1_species2`, `Twobody_species1_species3`, ...,
    * `total_conductivity`.
    * In total, there should be `2 + 2 * n_species + n_species * (n_species - 1) / 2` columns.
  * For conductivity with `-u std` or `-u var`, every conductivity column except `time` is followed by its uncertainty column:
    * `time`,
    * `MSD_self_species1`, `uncertainty_self_species1`, ...,
    * `MSD_cross_species1`, `uncertainty_cross_species1`, ...,
    * `Twobody_species1_species2`, `uncertainty_species1_species2`, ...,
    * `total_conductivity`, `uncertainty_total_conductivity`.
    * In total, there should be `2 + 4 * n_species + n_species * (n_species - 1)` columns.
* `-u/--uncertainty` is used to specify which uncertainties are present in the input file:
  * `none`: no uncertainties are given in the file.
  * `std`: the file contains standard deviations or standard errors directly.
  * `var`: the file contains variances, which are converted internally to standard deviations before the weighted fit.
The uncertainty is used only in the linear regression, not when identifying the linear regime in the MSD.
* `-c/--conductivity` is used to indicate that the input file contains conductivity data, and thus the program should calculate the conductivity instead of the diffusion coefficient (the latter is the default).
* `-l/--length` is used to specify the box length in pm, which is needed for a diffusion calculation.
Provide a single value for a cubic box, two values for a tetragonal box (`lx lz`, with `ly = lx`), or three values for a rectangular box.
The box length can also be read from a TRAVIS log file with `--from-travis`.
Boxes with angles different from 90° are not supported.
* `-o/--output` is used to specify the prefix of the output file, which will be a CSV file containing the results.
The output file will be named `<output_prefix>_out.csv` (default: `msdiff_out.csv`).
* `-s/--species` is used to specify the number of species in the system, which is needed to correctly parse the input file.
Defaults to 1 for diffusion and 2 for conductivity.
* `--hummer` expects up to three space-separated values to compute the Hummer correction term, which is used to extrapolate to infinite box size for cubic boxes.
The values are temperature in K, viscosity in kg/(m\*s), and the uncertainty of the viscosity in kg/(m\*s).
If only the temperature is given, the viscosity uncertainty defaults to zero.
If the viscosity is zero or omitted, the Hummer correction term is set to zero, similarly if the box length is zero.
* `-d/--dim/--dimensions` is used to specify the dimensionality of the system for the diffusion coefficient calculation, defaulting to 3.
* `--from-travis` is used to indicate that there is a corresponding TRAVIS log file `travis.log` in the same directory, which can be used to read the box length instead of providing `-l/--length`.
* `-z/--orthoboxy` is used to indicate that the MSD data provided in the input file (`-f/--file`) corresponds to movements in the x-y plane, while the second input file provided with this option corresponds to movements in the z direction, and that the [OrthoBoXY](https://doi.org/10.1021/acs.jpcb.3c04492) method should be used to calculate the diffusion coefficient.
* `-t/--tol/--tolerance` is used to specify the tolerance to identify the linear regime in the (logarithmic) MSD, which defaults to 0.1, meaning that the MSD data points are considered to be in the linear regime if they deviate by less than 10% from the linear fit.

## Diffusion

### Self-diffusion coefficient of NTf<sub>2</sub>

In [diffusion/ntf2](./diffusion/ntf2/), there is an [output file](./diffusion/ntf2/msd_ntf2.csv) from a TRAVIS MSD calculation of the anion in a system of [C<sub>2</sub>C<sub>1</sub>Im][NTf<sub>2</sub>] at 350 K.
The corresponding box length is 6134.48 pm.
At the given temperature, the viscosity of the system is estimated to be 8.277 mPa s, with an uncertainty of 5.039 mPa s, based on the equation in [this paper](https://doi.org/10.1021/jp044626d).
The program is run with the following command:

```bash
cd diffusion/ntf2
msdiff -f msd_ntf2.csv -l 6134.48 --hummer 350.0 0.008277 0.005039
```

The expected output is:

```
  MSDiff Diffusion
  ================

Species 1
Diffusion coefficient:           D_0 = (      20.986997 ±        0.000002) * 10^-12 m^2/s
Hummer correction term:          K   = (      14.325316 ±        8.721187) * 10^-12 m^2/s

Results written to msdiff_out.csv.
```
Additionally, the results can be found in the [MSDiff output file](./ntf2/msdiff_out.csv).

### Self-diffusion coefficient from averaged MSD

In [diffusion/standard_deviation](./diffusion/standard_deviation/), there is an [file](./diffusion/standard_deviation/msd_c2c1im_std.csv) that contains the MSD including standard deviation of each data point of the cation in a system of [C<sub>2</sub>C<sub>1</sub>Im][NTf<sub>2</sub>].
No Hummer correction is applied here (see output below).
To include the uncertainty in the linear regression, the `-u std` option is used:

```bash
cd diffusion/standard_deviation
msdiff -f msd_c2c1im_std.csv -u std
```

The expected output is:

```
  MSDiff Diffusion
  ================

Info: No box length given, set to zero. Hummer correction will be zero.

Species 1
Diffusion coefficient:           D_0 = (      37.250132 ±        0.021175) * 10^-12 m^2/s
Hummer correction term:          K   = (       0.000000 ±        0.000000) * 10^-12 m^2/s

Results written to msdiff_out.csv.
```

### Using the OrthoBoXY method

In [diffusion/orthoboxy](./diffusion/orthoboxy/), results from calculating the self-diffusion coefficient of water using the OrthoBoXY method are shown.
Two MSD files are provided, [one](./diffusion/orthoboxy/msd_H2O_#2_XY.csv) considering movements in the x-y plane and the [other](./diffusion/orthoboxy/msd_H2O_#2_Z.csv) considering movements in the z direction.
The corresponding dimensions of the tetragonal box are read from a TRAVIS output file, which is provided in the same directory.
The OrthoBoXY method also allows to determine the viscosity of the system if the simulation temperature is given through the `--hummer` option, which is 330 K in this case.
The program is run with the following command:

```bash
cd diffusion/orthoboxy
msdiff -f msd_H2O_#2_XY.csv -z msd_H2O_#2_Z.csv --from-travis --hummer 330
```

The expected output is:

```
  MSDiff Diffusion
  ================

Info: Box lengths read from travis.log: [1772.41, 1772.41, 4950.97] pm.

Info: OrthoBoXY mode assumes MSD in the input file to be in x and y directions and the additional file contains the MSD in the z direction.

0.2904487968443776
Species 1
Diffusion coefficient:           D_0 = (    5417.657463 ±        0.000107) * 10^-12 m^2/s
Diffusion coefficient (z):       D_z = (    4044.191494 ±        0.000214) * 10^-12 m^2/s
Hummer correction term:          K   = (       0.000000 ±        0.000000) * 10^-12 m^2/s
Viscosity:                       η   = (       0.290449 ±        0.000000) * 10^-3  Pa s

Results written to msdiff_out.csv.
```

## Conductivity

### A two-component system

In [conductivity/2_comp](./conductivity/2_comp/), there is an [output file](./conductivity/2_comp/conductivity_test_data.csv) from a TRAVIS conductivity calculation of a system of [C<sub>2</sub>C<sub>1</sub>Im][NTf<sub>2</sub>] without any uncertainties associated with the conductivity data.
The program is run with the following command:
```bash
cd conductivity/2_comp
msdiff -f conductivity_test_data.csv -c -u none
```

The expected output is:

```
  MSDiff Conductivity
  ===================

Note: If this is truly a binary system with no other (neutral or charged) species involved, the real transport numbers are dependent on the reference frame and bear no physical meaning.

Conductivity
Contribution          Sigma / S*m^-1    R^2 fit
msd_1_self       0.239279 ± 0.000008   0.999983
msd_2_self       0.419587 ± 0.000008   0.999923
msd_1_cross     -0.171835 ± 0.000008   0.999761
msd_2_cross      0.008690 ± 0.000008   0.245949
msd_1_2          0.339909 ± 0.000008   0.998192
total_eh         0.835629 ± 0.000008   0.998192

Linear regime identified between 4675.00 ps and 10224.00 ps, with 5550 data points used for the fit.

Transport Numbers
Species          t_ideal              t_real
1         0.363168 ± 0.000009  0.284095 ± 0.000011
2         0.636832 ± 0.000009  0.715905 ± 0.000011

Results written to msdiff_out.csv.
Transport numbers written to msdiff_tp.csv.
```
Note the very low R<sup>2</sup> value for the `msd_2_cross` contribution, which indicates that the linear fit is not good for this contribution, and thus the corresponding conductivity value should be interpreted with caution.

## A three-component system

In [conductivity/3_comp](./conductivity/3_comp/), there is an [output file](./conductivity/3_comp/conduct_3comp.csv) from a TRAVIS conductivity calculation of a system of three different ionic species, with variances given for all conductivity contributions.
The program is run with the following command:
```bash
cd conductivity/3_comp
msdiff -f conduct_3comp.csv -c -u var -s 3
```

The expected output is:

```
  MSDiff Conductivity
  ===================

Conductivity
Contribution          Sigma / S*m^-1    R^2 fit
msd_1_self       0.555349 ± 0.000304   0.999919
msd_2_self       0.075888 ± 0.000009   0.999994
msd_3_self       1.721330 ± 0.000630   0.999876
msd_1_cross     -0.010091 ± 0.002274   0.177452
msd_2_cross     -0.056834 ± 0.000077   0.999789
msd_3_cross      0.351561 ± 0.008135   0.976595
msd_1_2         -0.203851 ± 0.000887   0.997807
msd_1_3         -1.424095 ± 0.006024   0.994860
msd_2_3          0.274629 ± 0.001144   0.995243
total_eh         1.296666 ± 0.005284   0.996463

Linear regime identified between 18060.00 ps and 30000.00 ps, with 399 data points used for the fit.

Transport Numbers
Species          t_ideal              t_real
1         0.236061 ± 0.000117 -0.209298 ± 0.004218
2         0.032258 ± 0.000010  0.042405 ± 0.000622
3         0.731682 ± 0.000119  1.166893 ± 0.004034

Results written to msdiff_out.csv.
Transport numbers written to msdiff_tp.csv.
```
