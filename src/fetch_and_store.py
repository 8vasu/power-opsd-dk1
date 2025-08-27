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
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert

# ------------------------------
# 1) Database credentials from .env
# ------------------------------
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = 5432

# SQLAlchemy engine
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ------------------------------
# 2) OPSD dataset URL & local cache
# ------------------------------
CSV_URL = "https://data.open-power-system-data.org/time_series/2020-10-06/time_series_60min_singleindex.csv"
CACHE_FILE_DIRNAME = "data"
CACHE_FILE_DIR = f"../{CACHE_FILE_DIRNAME}"
CACHE_FILENAME = "time_series_60min.csv"
CACHE_FILE = f"{CACHE_FILE_DIR}/{CACHE_FILENAME}"
CACHE_FILE_PATH_TO_SHOW = f"{CACHE_FILE_DIRNAME}/{CACHE_FILENAME}"  # For user-friendly display

# ------------------------------
# 3) Main function
# ------------------------------
def main():
    # 3a) Load CSV (cache if exists)
    if os.path.exists(CACHE_FILE):
        print(f"Loading cached CSV from {CACHE_FILE_PATH_TO_SHOW} ...")
        df = pd.read_csv(CACHE_FILE, index_col=0, parse_dates=True)
    else:
        print(f"Downloading OPSD dataset from {CSV_URL} ...")
        df = pd.read_csv(CSV_URL, index_col=0, parse_dates=True)
        os.makedirs(CACHE_FILE_DIR, exist_ok=True)
        df.to_csv(CACHE_FILE)
        print(f"Saved CSV to {CACHE_FILE_PATH_TO_SHOW}")

    # 3b) Filter DK1 day-ahead prices
    dk1_col = "DK_1_price_day_ahead"
    if dk1_col not in df.columns:
        raise ValueError(f"Column {dk1_col} not found. Available: {list(df.columns)}")

    dk1 = df[[dk1_col]].dropna().rename(columns={dk1_col: "price_eur_per_mwh"})
    dk1.reset_index(inplace=True)
    dk1.rename(columns={"utc_timestamp": "ts"}, inplace=True)

    print(f"Inserting {len(dk1)} rows into database ...")

    # ------------------------------
    # 3c) Conflict-safe insertion into TimescaleDB
    # ------------------------------
    metadata = MetaData()
    metadata.reflect(engine)  # SQLAlchemy 2.x style
    dk1_table = Table('dk1_prices', metadata, autoload_with=engine)

    records = dk1.to_dict(orient='records')
    stmt = insert(dk1_table).values(records)
    stmt = stmt.on_conflict_do_nothing(index_elements=['ts'])

    with engine.begin() as conn:
        conn.execute(stmt)

    print("Done.")

# ------------------------------
# 4) Entry point
# ------------------------------
if __name__ == "__main__":
    main()
