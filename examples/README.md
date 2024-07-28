# Examples for MSDiff

This directory contains example files and their expected results.

## Example 1

In [ntf2](./ntf2/), there is an [output file](./ntf2/msd_from_travis.csv) from a TRAVIS MSD calculation of a system of [EMIM][NTF2] at 350 K. 
The corresponding box length is 6134.48 pm.
The program is run with the following command:

```
cd ntf2
msdiff -f msd_from_travis.csv -l 6134.48 -t 350
```

The expected output is:

```
  MSDiff results
  ==============
Analyzed 1 data sets:
Diffusion coefficient: 		 D = (21.20593745 ± 0.00786019) * 10^-12 m^2/s
Hummer correction term: 	 K = (15.06615800 ± 0.00000000) * 10^-12 m^2/s

Individual results written to msdiff_mols.csv
Average results written to msdiff_out.csv
```
Additionally, the results can be found in the [MSDiff output file](./ntf2/msdiff_out.csv).
