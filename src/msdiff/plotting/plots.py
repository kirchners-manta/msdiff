"""
Plotting functions for MSD and fits.
"""

from __future__ import annotations

import lmfit
import matplotlib.pyplot as plt
import pandas as pd

lmod = lmfit.models.LinearModel()


def generate_simple_plot(
    data: pd.DataFrame, firststep: int
) -> None:  # pragma: no cover
    """Generate a simple plot of the MSD data and the fitting region

    Parameters
    ----------
    data : pd.DataFrame
        MSD data
    firststep : int
        First step of the linear region, not its index
    """
    # generate a figure object with a single axis
    fig = plt.figure(figsize=(4.5, 4.5))
    gs = fig.add_gridspec(1, 1)
    ax = fig.add_subplot(gs[0, 0])

    # add fit to plot
    msd_data = data[data["time"] >= data["time"][firststep]]
    init = lmod.guess(data=msd_data["msd"], x=msd_data["time"])
    out = lmod.fit(data=msd_data["msd"], x=msd_data["time"], params=init)
    dely = out.eval_uncertainty(sigma=3, x=msd_data["time"])

    # plot
    ax.plot(
        data["time"], data["msd"], color="black", linewidth=1, alpha=0.3, label="data"
    )
    ax.plot(
        data["time"][firststep:],
        data["msd"][firststep:],
        color="black",
        linewidth=1,
        alpha=1,
        label="used for fit",
    )
    ax.axvline(
        data["time"][firststep], color="k", linewidth=1, linestyle=":", alpha=0.5
    )
    ax.fill_between(
        msd_data["time"],
        out.best_fit - dely,
        out.best_fit + dely,
        color="red",
        alpha=0.5,
        label=r"3$\sigma$ confidence interval",
    )

    ax.set_xlabel(r"$\tau$ / ps")
    ax.set_ylabel(r"MSD / pm$^2$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(loc="upper left")

    fig.savefig("msdiff_plot.pdf", dpi=300, bbox_inches="tight", format="pdf")
