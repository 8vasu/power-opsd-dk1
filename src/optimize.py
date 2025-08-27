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

import os
import pandas as pd
import cvxpy as cp
from sqlalchemy import create_engine

TUNING_PARAM = 50  # Adjust this parameter to balance total cost vs. smoothness
NUM_OLDEST_RECS = 1000  # Number of oldest records to fetch from DB

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = 5432

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def main():
    print("Loading DK1 price data from DB ...")
    df = pd.read_sql(f"SELECT * FROM dk1_prices ORDER BY ts ASC LIMIT {NUM_OLDEST_RECS};", engine)

    prices = df["price_eur_per_mwh"].values
    n = len(prices)

    # Quadratic optimization: minimize cost + smoothness
    x = cp.Variable(n)
    objective = cp.Minimize(cp.sum(cp.multiply(prices, x)) + TUNING_PARAM * cp.sum_squares(x[1:] - x[:-1]))
    constraints = [x >= 0, cp.sum(x) == 100]
    prob = cp.Problem(objective, constraints)
    prob.solve()

    df["allocation"] = x.value
    os.makedirs("../data", exist_ok=True)
    df.to_csv("../data/optimized.csv", index=False)
    print("Optimization complete. Results saved to data/optimized.csv.")

if __name__ == "__main__":
    main()
