import io
import os
import time
from pathlib import Path
import requests
import pandas as pd

JHU_BASE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"
FILES = {
    "confirmed": "time_series_covid19_confirmed_global.csv",
    "deaths": "time_series_covid19_deaths_global.csv",
    "recovered": "time_series_covid19_recovered_global.csv",  # some regions may be missing later; optional
}

DATA_RAW = Path("data/raw")
DATA_PROCESSED = Path("data/processed")
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

def _download_csv(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))

def _melt_wide(df: pd.DataFrame, value_name: str) -> pd.DataFrame:
    id_cols = ["Province/State", "Country/Region", "Lat", "Long"]
    date_cols = [c for c in df.columns if c not in id_cols]
    out = df.melt(id_vars=id_cols, value_vars=date_cols, var_name="date", value_name=value_name)
    out["date"] = pd.to_datetime(out["date"])
    out.rename(columns={"Country/Region": "country", "Province/State": "province", "Lat": "lat", "Long": "lon"}, inplace=True)
    return out

def fetch_and_process(include_recovered: bool = False):
    # 1) Download
    dfs = {}
    for k, fname in FILES.items():
        if (k == "recovered") and not include_recovered:
            continue
        url = f"{JHU_BASE}/{fname}"
        df = _download_csv(url)
        df.to_csv(DATA_RAW / fname, index=False)
        dfs[k] = df

    # 2) Reshape to long & merge
    long_parts = []
    if "confirmed" in dfs:
        long_parts.append(_melt_wide(dfs["confirmed"], "confirmed"))
    if "deaths" in dfs:
        long_parts.append(_melt_wide(dfs["deaths"], "deaths"))
    if "recovered" in dfs:
        long_parts.append(_melt_wide(dfs["recovered"], "recovered"))

    # Merge on keys
    base = long_parts[0]
    for nxt in long_parts[1:]:
        base = base.merge(nxt[["country", "province", "date", nxt.columns[-1]]],
                          on=["country", "province", "date"], how="outer")

    # 3) Fill NA and compute daily metrics
    df = base.sort_values(["country", "province", "date"]).copy()
    for col in ["confirmed", "deaths", "recovered"]:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype("Int64")

    # Aggregate to country level
    country_daily = (df
        .groupby(["country", "date"], as_index=False)[[c for c in ["confirmed","deaths","recovered"] if c in df.columns]]
        .sum()
        .sort_values(["country","date"])
    )

    # Daily new cases/deaths
    for col in ["confirmed","deaths"]:
        if col in country_daily.columns:
            dcol = f"new_{col}"
            country_daily[dcol] = country_daily.groupby("country")[col].diff().fillna(0).clip(lower=0).astype("Int64")

    # 7-day rolling averages
    for col in ["new_confirmed","new_deaths"]:
        if col in country_daily.columns:
            rcol = f"{col}_7dma"
            country_daily[rcol] = (country_daily
                                   .groupby("country")[col]
                                   .transform(lambda s: s.rolling(7, min_periods=1).mean()))

    # Case fatality rate
    if set(["confirmed","deaths"]).issubset(country_daily.columns):
        country_daily["cfr"] = (country_daily["deaths"] / country_daily["confirmed"]).replace([float("inf")], 0)

    # Global aggregates
    global_daily = (country_daily
        .groupby("date", as_index=False)
        .sum(numeric_only=True)
        .sort_values("date")
    )
    # Keep CFR as global_deaths/global_confirmed
    if set(["confirmed","deaths"]).issubset(country_daily.columns):
        g = country_daily.groupby("date", as_index=False)[["confirmed","deaths"]].sum()
        global_daily["cfr"] = (g["deaths"] / g["confirmed"]).replace([float("inf")], 0)

    # Save processed
    ts = int(time.time())
    country_daily.to_csv(DATA_PROCESSED / "country_daily.csv", index=False)
    global_daily.to_csv(DATA_PROCESSED / "global_daily.csv", index=False)
    print(f"Saved processed files at {DATA_PROCESSED} (timestamp {ts}).")

if __name__ == "__main__":
    fetch_and_process(include_recovered=False)
