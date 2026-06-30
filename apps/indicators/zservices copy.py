import pandas as pd
import requests
from django.conf import settings
from pathlib import Path

# =========================================================
# GEOJSON COUNTRY LOOKUP FROM CSV (MATCH API ISO3 CODES)
# =========================================================
countries_csv = (
    Path(settings.BASE_DIR)
    / "static"
    / "data"
    / "csv"
    / "countries.csv"
)

countries_df = pd.read_csv(countries_csv)
countries_df.columns = countries_df.columns.str.strip()

countries_lookup = dict(zip(countries_df["iso3"], countries_df["country"]))
valid_iso3_codes = set(countries_df["iso3"])
country_meta = countries_df.set_index("iso3")[[
    "continent",
    "INCOME_GRP",
    "REGION_WB"
]].to_dict(orient="index")

# =========================================================
# WORLD BANK: CHILD MORTALITY (accepts year parameter)
# =========================================================

def get_child_mortality(year=2023):
    """
    Fetch under‑5 mortality data for a given year from the World Bank API.
    Returns a pandas DataFrame with country details and mortality value.
    """
    url = (
        "https://api.worldbank.org/v2/"
        "country/all/"
        "indicator/SH.DYN.MORT"
        "?format=json"
        f"&per_page=20000"
        f"&date={year}:{year}"          # single year range
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

        if not iso3 or iso3 not in valid_iso3_codes or value is None:
            continue

        meta = country_meta.get(iso3, {})
        rows.append({
            "iso3": iso3,
            "country": countries_lookup.get(iso3),
            "continent": meta.get("continent"),
            "income_group": meta.get("INCOME_GRP"),
            "subregion": meta.get("REGION_WB"),
            "year": int(row["date"]),
            "mortality": float(value)
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("mortality", ascending=False)
    return df

#
# GET CHILD MORTALITY FOR A RANGE OF YEARS (1960-2024)
#
def get_child_mortality_range(start_year=1960, end_year=2024):
    """
    Fetch under‑5 mortality data for a range of years from the World Bank API.
    Returns a pandas DataFrame with all years.
    """
    url = (
        "https://api.worldbank.org/v2/"
        "country/all/"
        "indicator/SH.DYN.MORT"
        "?format=json"
        f"&per_page=20000"
        f"&date={start_year}:{end_year}"
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
        year_str = row.get("date")

        if not iso3 or iso3 not in valid_iso3_codes or value is None or year_str is None:
            continue

        meta = country_meta.get(iso3, {})
        rows.append({
            "iso3": iso3,
            "country": countries_lookup.get(iso3),
            "continent": meta.get("continent"),
            "income_group": meta.get("INCOME_GRP"),
            "subregion": meta.get("REGION_WB"),
            "year": int(year_str),
            "mortality": float(value)
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["year", "mortality"], ascending=[True, False])
    return df

