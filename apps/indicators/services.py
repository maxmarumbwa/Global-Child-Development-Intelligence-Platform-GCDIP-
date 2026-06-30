import pandas as pd
import requests
from django.conf import settings
from pathlib import Path
from django.core.cache import cache
import json

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
# INDICATOR NAMES MAPPING
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
    'SH.STA.ANV4.ZS': 'Prenatal ≥4 visits',
    'SH.STA.ANVC.ZS': 'Prenatal care %',
    'SH.STA.BRTC.ZS': 'Skilled birth attendance',
    'SH.IMM.HEPB': 'HepB3 immunization',
    'SH.IMM.HIB3': 'Hib3 immunization',
    'SH.IMM.IBCG': 'BCG immunization',
    'SH.IMM.IDPT': 'DPT immunization',
    'SH.IMM.MEAS': 'Measles immunization',
    'SH.STA.ARIF.ZS': 'ARI prevalence',
    'SH.STA.ORTH': 'Diarrhea treatment ORS',
    'SH.H2O.BASW.ZS': 'Basic drinking water',
    'SH.STA.ACSN': 'Improved sanitation',
    'SH.STA.ODFC.ZS': 'Open defecation',
    'SH.STA.SMSS.ZS': 'Safely managed sanitation',
    'SL.TLF.0714.ZS': 'Children in employment',
    'SL.TLF.0714.SW.TM': 'Work hrs (study+work)',
    'SL.TLF.0714.SW.ZS': 'Employment & study',
    'SL.AGR.0714.ZS': 'Child labor in agriculture',
    'SL.FAM.0714.FE.ZS': 'Unpaid family workers',
    'SL.MNF.0714.ZS': 'Child labor in manufacturing',
    'SH.STA.FGMS.ZS': 'FGM prevalence',
    'SP.M15.2024.FE.ZS': 'Married by 15',
    'SP.M18.2024.FE.ZS': 'Married by 18',
    'SE.ENR.ORPH': 'Orphan school attendance ratio',
    'ID.OWN.BRTH.ZS': 'Birth certification',
    'SP.REG.BRTH.RU.ZS': 'Completeness, rural',
    'SP.REG.BRTH.UR.ZS': 'Completeness, urban',
    'SH.STA.BFED.ZS': 'Exclusive breastfeeding',
    'SH.STA.BRTW.ZS': 'Low birthweight',
    'SH.STA.OWGH.MA.ZS': 'Overweight, male',
    'SH.STA.STNT.ZS': 'Stunting',
    'SH.STA.WAST.ZS': 'Wasting',
    'HD.HCI.STNT': 'Fraction not stunted',
}

def get_indicator_name(code):
    """Return human-readable name for indicator code."""
    return INDICATOR_NAMES.get(code, code)

# =========================================================
# GENERIC INDICATOR FETCHER WITH CACHING
# =========================================================

def fetch_indicator_data(indicator_code, start_year=1960, end_year=2024):
    """
    Fetch data for any World Bank indicator for a range of years.
    Uses Django cache to avoid repeated API calls.
    """
    cache_key = f"indicator_{indicator_code}_{start_year}_{end_year}"
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        print(f"✅ Using cached data for {indicator_code}")
        return pd.DataFrame(cached_data)
    
    print(f"🔄 Fetching data for {indicator_code} from API...")
    
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
        # Cache for 1 hour
        cache.set(cache_key, df.to_dict('records'), 3600)
    
    return df