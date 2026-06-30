import pandas as pd
import requests
from django.conf import settings
from pathlib import Path
import time

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
# GENERIC INDICATOR FETCHER
# =========================================================

def get_indicator_data(indicator_code, year=2023):
    """
    Fetch data for any World Bank indicator for a given year.
    Returns a pandas DataFrame with country details and indicator value.
    """
    url = (
        "https://api.worldbank.org/v2/"
        "country/all/"
        f"indicator/{indicator_code}"
        "?format=json"
        f"&per_page=20000"
        f"&date={year}:{year}"
    )

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data for {indicator_code}: {e}")
        return pd.DataFrame()

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
            "value": float(value)  # Use 'value' instead of 'mortality' for generic
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("value", ascending=False)
    return df

def get_indicator_data_range(indicator_code, start_year=1960, end_year=2024):
    """
    Fetch data for a World Bank indicator for a range of years.
    Returns a pandas DataFrame with all years.
    """
    url = (
        "https://api.worldbank.org/v2/"
        "country/all/"
        f"indicator/{indicator_code}"
        "?format=json"
        f"&per_page=20000"
        f"&date={start_year}:{end_year}"
    )

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data for {indicator_code}: {e}")
        return pd.DataFrame()

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
            "value": float(value)
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["year", "value"], ascending=[True, False])
    return df

# =========================================================
# BACKWARD COMPATIBILITY (Maintain existing function names)
# =========================================================

def get_child_mortality(year=2023):
    """Backward compatibility wrapper."""
    df = get_indicator_data('SH.DYN.MORT', year)
    if not df.empty:
        df = df.rename(columns={'value': 'mortality'})
    return df

def get_child_mortality_range(start_year=1960, end_year=2024):
    """Backward compatibility wrapper."""
    df = get_indicator_data_range('SH.DYN.MORT', start_year, end_year)
    if not df.empty:
        df = df.rename(columns={'value': 'mortality'})
    return df

# =========================================================
# HELPER: Get indicator display name
# =========================================================

INDICATOR_NAMES = {
    'SH.DTH.MORT': 'Number of under-five deaths',
    'SH.DTH.IMRT': 'Number of infant deaths',
    'SH.DTH.STLB': 'Number of stillbirths',
    'SH.DTH.NMRT': 'Number of neonatal deaths',
    'SH.DYN.STLB': 'Stillbirth rate (per 1,000 total births)',
    'SH.DYN.MORT': 'Under‑5 mortality rate',
    'SH.DYN.0509': '5‑9 mortality (per 1,000)',
    'SH.MMR.DTHS': 'Number of maternal deaths',
    'SH.DYN.MORT.FE': 'Under‑5 mortality rate (female)',
    'SH.DYN.MORT.MA': 'Under‑5 mortality rate (male)',
}

def get_indicator_name(code):
    """Return human-readable name for indicator code."""
    return INDICATOR_NAMES.get(code, code)