# Examples for MSDiff

This directory contains example files and their expected results.

## Self-diffusion coefficient of NTf<sub>2</sub>

In [diffusion/ntf2](./diffusion/ntf2/), there is an [output file](./diffusion/ntf2/msd_from_travis.csv) from a TRAVIS MSD calculation of the anion in a system of [C<sub>2</sub>C<sub>1</sub>Im][NTf<sub>2</sub>] at 350 K.
The corresponding box length is 6134.48 pm. 
The program is run with the following command:

```bash
cd diffusion/ntf2
msdiff -f msd_from_travis.csv -l 6134.48 --hummer 350.0
```

The expected output is:

```
  MSDiff Diffusion
  ================
Diffusion coefficient:           D_0 = (      20.931123 ±        0.003736) * 10^-12 m^2/s
Hummer correction term:          K   = (      14.325316 ±        8.721187) * 10^-12 m^2/s
Results written to msdiff_out.csv
```
Additionally, the results can be found in the [MSDiff output file](./ntf2/msdiff_out.csv). 
Please note that in this example, the `--hummer` option is used to calculate the Hummer correction term, where the temperature is set to 350 K, while the viscosity and its uncertainty are not given, thus falling back to the default values.

## Self-diffusion coefficient from averaged MSD

In [diffusion/avg](./diffusion/avg/), there is an [file](./diffusion/avg/diffusion_c2c1im_avg.csv) that contains the averaged MSD and standard deviation of several trajectories of the cation in a system of [C<sub>2</sub>C<sub>1</sub>Im][NTf<sub>2</sub>].
The corresponding box length is 4869.95 pm.
As this is an averaged MSD the `--avg` option is selected, and the program is run with the following command:

```bash
cd diffusion/avg
msdiff -f diffusion_c2c1im_avg.csv -l 4869.95 --avg
```

The expected output is:

```
  MSDiff Diffusion
  ================
Diffusion coefficient:           D_0 = (      35.175876 ±        0.003846) * 10^-12 m^2/s
Hummer correction term:          K   = (      18.045024 ±       10.985729) * 10^-12 m^2/s
Results written to msdiff_out.csv
```

## Self-diffusion coefficient from MSD using the OrthoBoXY method

In [diffusion/orthoboxy](./diffusion/orthoboxy/), results from calculating the self-diffusion coefficient of water at 330 K using the OrthoBoXY method are shown.
Two MSD files are provided, one considering movements in the x-y plane and the other considering movements in the z direction.
The corresponding box length is read from a TRAVIS output file, which is provided in the same directory.
The program is run with the following command:

```bash
cd diffusion/orthoboxy
msdiff -f msd_H2O_#2_XY.csv --orthoboxy msd_H2O_#2_Z.csv --from-travis --hummer 330
```

The expected output is:

```
  MSDiff Diffusion
  ================
Diffusion coefficient:           D_0 = (    5417.100506 ±        2.583906) * 10^-12 m^2/s
Diffusion coefficient (z):       D_z = (    4044.697511 ±        2.689416) * 10^-12 m^2/s
Hummer correction term:          K   = (       0.000000 ±        0.000000) * 10^-12 m^2/s
Viscosity:                       η   = (       0.290674 ±        0.000790) * 10^-3  Pa s
Results written to msdiff_out.csv
```

## Conductivity from (averaged) collective MSD

Next, in [conductivity/avg](./conductivity/avg/), there is an [file](./conductivity/avg/conductivity_avg.csv) that contains the averaged collective MSD and standard deviation of several trajectories of the system of [C<sub>2</sub>C<sub>1</sub>Im][NTf<sub>2</sub>].
To calculate the conductivity, the `-c` option needs to be called, but no box length is needed.

```bash
cd conductivity/avg
msdiff -f conductivity_avg.csv -c --avg
```

This should yield the following output:

```
  MSDiff Conductivity
  ===================

Contributions to the conductivity
anion self             :   0.2515 ±  0.0000 S/m
anion cross            :  -0.2062 ±  0.0001 S/m
anion total            :   0.0488 ±  0.0000 S/m
cation self            :   0.4249 ±  0.0000 S/m
cation cross           :  -0.1171 ±  0.0000 S/m
cation total           :   0.3103 ±  0.0001 S/m
anion-cation           :   0.2462 ±  0.0001 S/m
Nernst-Einstein        :   0.6766 ±  0.0001 S/m
Einstein-Helfand       :   0.6051 ±  0.0001 S/m

A posteriori quantities
ionicity   :   0.8944 ±  0.0002
t_mm_ideal :   0.3717 ±  0.0001
t_pp_ideal :   0.6281 ±  0.0001
t_mm       :   0.2840 ±  0.0001
t_pp       :   0.7161 ±  0.0002

Results written to msdiff_out.csv
A posteriori quantities written to msdiff_post.csv
```

As a note, the tolerance used to identify the linear regime in the MSD, defaults to 0.1, but can be changed with the `--tol` option.
