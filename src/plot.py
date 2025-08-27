#!/usr/bin/python3

# Copyright (C) 2025 Soumendra Ganguly

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pandas as pd
import matplotlib.pyplot as plt
import os

def main():
    df = pd.read_csv("../data/optimized.csv", parse_dates=["ts"])

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(df["ts"], df["price_eur_per_mwh"], color="blue", label="Price (EUR/MWh)")
    ax1.set_ylabel("Price (EUR/MWh)", color="blue")

    ax2 = ax1.twinx()
    ax2.bar(df["ts"], df["allocation"], alpha=0.3, color="orange", label="Optimized allocation")
    ax2.set_ylabel("Allocation", color="orange")

    plt.title("DK1 Prices and Optimized Allocation (24h)")
    fig.tight_layout()
    os.makedirs("../plots", exist_ok=True)
    plt.savefig("../plots/plot.png")
    print("Plot saved to plots/plot.png")

if __name__ == "__main__":
    main()
