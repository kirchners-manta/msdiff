"""
Useful functions for the diffusion coefficient calculation.
"""

import numpy as np
import pandas as pd
from lmfit.models import LinearModel

lmod = LinearModel()

def find_linear_region(data: pd.DataFrame, tol: float) -> int:

    inlinreg = True
    timestepskip = 500
    numskip = 1
    maxtime = len(data["time"])
    while inlinreg == True:
        if numskip * timestepskip + 1 > maxtime:
            firststep = maxtime - 1 - (numskip - 1) * timestepskip
            inlinreg = False
            print("caught")
            return firststep
        else:
            t1 = maxtime - 1 - (numskip - 1) * timestepskip
            t2 = maxtime - 1 - numskip * timestepskip
            slope = (data["msd"][t1] - data["msd"][t2]) / (data["time"][t1] - data["time"][t2])
            print("slope: ", slope, "numskip:" , numskip)
            if (slope -1) > tol:
                inlinreg = False
                firststep = t1
                return firststep
            else:
                numskip += 1

    return firststep

def perform_linear_regression(data: pd.DataFrame, firststep: int) -> None:

    # select data for fitting according from linear region
    msd = data[data["time"] >= data["time"][firststep]]

    # initial guess to improve the fit
    init = lmod.guess(data=msd["msd"], x=msd["time"])
    # perform the fit
    fit = lmod.fit(data=msd["msd"], x=msd["time"], params=init)
    print(type(fit))

    # return fit

def calc_Hummer_correction(temp: float, viscosity:float, box_length: float) -> float:

    xi = 2.837298  # dimensionless
    kb = 1.38064852e-23  # Boltzmann constant in J/K
    # calculate the Hummer correction term
    corr = kb * xi * temp * 1e24 / (6 * np.pi * viscosity * box_length)

    return corr
