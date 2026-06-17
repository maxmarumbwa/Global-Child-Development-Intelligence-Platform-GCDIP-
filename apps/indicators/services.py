import pandas as pd
import requests
from django.conf import settings
from pathlib import Path


# =========================================================
#GEOJSON COUNTRY LOOKUP FROM CSV (MATCH API ISO3 CODES)
# =========================================================
countries_csv = (
    Path(settings.BASE_DIR)
    / "static"
    / "data"
    / "csv"
    / "countries.csv"
)

countries_df = pd.read_csv(countries_csv)

countries_lookup = dict(
    zip(
        countries_df["iso3"],
        countries_df["country"]
    )
)

valid_iso3_codes = set(
    countries_df["iso3"]
)


# =========================================================
# WORLD BANK: CHILD MORTALITY
# =========================================================

def get_child_mortality():

    url = (
        "https://api.worldbank.org/v2/"
        "country/all/"
        "indicator/SH.DYN.MORT"
        "?format=json"
        "&per_page=20000"
        "&date=2023:2023"
    )

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    rows = []

    if len(data) < 2:
        return pd.DataFrame()

    for row in data[1]:

        iso3 = row.get("countryiso3code")
        value = row.get("value")

        if not iso3:
            continue

        if iso3 not in valid_iso3_codes:
            continue

        if value is None:
            continue

        rows.append({
            "iso3": iso3,
            "country": countries_lookup.get(iso3),
            "year": int(row["date"]),
            "mortality": float(value)
        })

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(
            "mortality",
            ascending=False
        )

    return df