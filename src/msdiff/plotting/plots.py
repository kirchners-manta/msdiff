"""
Plotting functions for MSD and fits.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def generate_simple_plot(
    data: pd.DataFrame, firststep: int
) -> None:  # pragma: no cover
    # generate a figure object with a single axis
    fig = plt.figure(figsize=(4.5, 4.5))
    gs = fig.add_gridspec(1, 1)
    ax = fig.add_subplot(gs[0, 0])

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

    ax.set_xlabel(r"$\tau$ / ps")
    ax.set_ylabel(r"MSD / pm$^2$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend(loc="upper left")

    fig.savefig("msdiff_plot.pdf", dpi=300, bbox_inches="tight", format="pdf")
