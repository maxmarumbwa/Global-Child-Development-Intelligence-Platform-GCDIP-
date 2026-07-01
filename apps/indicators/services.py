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
# INDICATOR METADATA WITH COLOR SCHEMES
# =========================================================
INDICATOR_METADATA = {
    # ============================================================
    # MORTALITY & MATERNAL HEALTH (Reds/Oranges)
    # ============================================================
    'SH.DTH.MORT': {
        'name': 'Number of under-five deaths',
        'color_scheme': 'reds',
        'category': 'Mortality',
        'unit': 'count',
        'description': 'Total number of deaths among children under 5 years of age'
    },
    'SH.DTH.IMRT': {
        'name': 'Number of infant deaths',
        'color_scheme': 'reds',
        'category': 'Mortality',
        'unit': 'count',
        'description': 'Total number of deaths among infants under 1 year of age'
    },
    'SH.DTH.STLB': {
        'name': 'Number of stillbirths',
        'color_scheme': 'reds',
        'category': 'Mortality',
        'unit': 'count',
        'description': 'Total number of stillbirths (fetal deaths after 28 weeks)'
    },
    'SH.DTH.NMRT': {
        'name': 'Number of neonatal deaths',
        'color_scheme': 'reds',
        'category': 'Mortality',
        'unit': 'count',
        'description': 'Total number of deaths among newborns (0-28 days)'
    },
    'SH.DYN.STLB': {
        'name': 'Stillbirth rate (per 1,000 total births)',
        'color_scheme': 'oranges',
        'category': 'Mortality',
        'unit': 'per 1,000 births',
        'description': 'Number of stillbirths per 1,000 total births'
    },
    'SH.DYN.MORT': {
        'name': 'Under‑5 mortality rate',
        'color_scheme': 'oranges',
        'category': 'Mortality',
        'unit': 'per 1,000 live births',
        'description': 'Probability of dying between birth and age 5 per 1,000 live births'
    },
    'SH.DYN.0509': {
        'name': '5‑9 mortality (per 1,000)',
        'color_scheme': 'oranges',
        'category': 'Mortality',
        'unit': 'per 1,000',
        'description': 'Mortality rate for children aged 5-9 years per 1,000'
    },
    'SH.MMR.DTHS': {
        'name': 'Number of maternal deaths',
        'color_scheme': 'reds',
        'category': 'Mortality',
        'unit': 'count',
        'description': 'Total number of maternal deaths during pregnancy and childbirth'
    },

    # ============================================================
    # ANTENATAL & MATERNAL CARE (Greens)
    # ============================================================
    'SH.STA.ANV4.ZS': {
        'name': 'Prenatal ≥4 visits',
        'color_scheme': 'greens',
        'category': 'Maternal Care',
        'unit': '%',
        'description': 'Percentage of women with at least 4 antenatal care visits'
    },
    'SH.STA.ANVC.ZS': {
        'name': 'Prenatal care %',
        'color_scheme': 'greens',
        'category': 'Maternal Care',
        'unit': '%',
        'description': 'Percentage of women receiving any prenatal care'
    },
    'SH.STA.BRTC.ZS': {
        'name': 'Skilled birth attendance',
        'color_scheme': 'greens',
        'category': 'Maternal Care',
        'unit': '%',
        'description': 'Percentage of births attended by skilled health personnel'
    },

    # ============================================================
    # CHILD HEALTH & IMMUNIZATION (Blues)
    # ============================================================
    'SH.IMM.HEPB': {
        'name': 'HepB3 immunization',
        'color_scheme': 'blues',
        'category': 'Immunization',
        'unit': '%',
        'description': 'Percentage of children immunized against Hepatitis B (3 doses)'
    },
    'SH.IMM.HIB3': {
        'name': 'Hib3 immunization',
        'color_scheme': 'blues',
        'category': 'Immunization',
        'unit': '%',
        'description': 'Percentage of children immunized against Hib (3 doses)'
    },
    'SH.IMM.IBCG': {
        'name': 'BCG immunization',
        'color_scheme': 'blues',
        'category': 'Immunization',
        'unit': '%',
        'description': 'Percentage of children immunized with BCG vaccine'
    },
    'SH.IMM.IDPT': {
        'name': 'DPT immunization',
        'color_scheme': 'blues',
        'category': 'Immunization',
        'unit': '%',
        'description': 'Percentage of children immunized with DPT vaccine (3 doses)'
    },
    'SH.IMM.MEAS': {
        'name': 'Measles immunization',
        'color_scheme': 'blues',
        'category': 'Immunization',
        'unit': '%',
        'description': 'Percentage of children immunized against measles'
    },
    'SH.STA.ARIF.ZS': {
        'name': 'ARI prevalence',
        'color_scheme': 'purples',
        'category': 'Child Health',
        'unit': '%',
        'description': 'Percentage of children with Acute Respiratory Infection'
    },
    'SH.STA.ORTH': {
        'name': 'Diarrhea treatment ORS',
        'color_scheme': 'purples',
        'category': 'Child Health',
        'unit': '%',
        'description': 'Percentage of children with diarrhea receiving ORS treatment'
    },

    # ============================================================
    # WASH (Teals/Blues)
    # ============================================================
    'SH.H2O.BASW.ZS': {
        'name': 'Basic drinking water',
        'color_scheme': 'blues',
        'category': 'WASH',
        'unit': '%',
        'description': 'Percentage of population using basic drinking water services'
    },
    'SH.STA.ACSN': {
        'name': 'Improved sanitation',
        'color_scheme': 'teals',
        'category': 'WASH',
        'unit': '%',
        'description': 'Percentage of population using improved sanitation facilities'
    },
    'SH.STA.ODFC.ZS': {
        'name': 'Open defecation',
        'color_scheme': 'oranges',
        'category': 'WASH',
        'unit': '%',
        'description': 'Percentage of population practicing open defecation'
    },
    'SH.STA.SMSS.ZS': {
        'name': 'Safely managed sanitation',
        'color_scheme': 'teals',
        'category': 'WASH',
        'unit': '%',
        'description': 'Percentage of population using safely managed sanitation services'
    },

    # ============================================================
    # CHILD LABOR (Oranges)
    # ============================================================
    'SL.TLF.0714.ZS': {
        'name': 'Children in employment',
        'color_scheme': 'oranges',
        'category': 'Child Labor',
        'unit': '%',
        'description': 'Percentage of children aged 7-14 engaged in employment'
    },
    'SL.TLF.0714.SW.TM': {
        'name': 'Work hrs (study+work)',
        'color_scheme': 'purples',
        'category': 'Child Labor',
        'unit': 'hours',
        'description': 'Average hours worked including study+work for children 7-14'
    },
    'SL.TLF.0714.SW.ZS': {
        'name': 'Employment & study',
        'color_scheme': 'purples',
        'category': 'Child Labor',
        'unit': '%',
        'description': 'Percentage of children combining employment and study'
    },
    'SL.AGR.0714.ZS': {
        'name': 'Child labor in agriculture',
        'color_scheme': 'oranges',
        'category': 'Child Labor',
        'unit': '%',
        'description': 'Percentage of children engaged in agricultural labor'
    },
    'SL.FAM.0714.FE.ZS': {
        'name': 'Unpaid family workers',
        'color_scheme': 'oranges',
        'category': 'Child Labor',
        'unit': '%',
        'description': 'Percentage of children working as unpaid family workers'
    },
    'SL.MNF.0714.ZS': {
        'name': 'Child labor in manufacturing',
        'color_scheme': 'oranges',
        'category': 'Child Labor',
        'unit': '%',
        'description': 'Percentage of children engaged in manufacturing labor'
    },

    # ============================================================
    # HARMFUL PRACTICES (Reds)
    # ============================================================
    'SH.STA.FGMS.ZS': {
        'name': 'FGM prevalence',
        'color_scheme': 'reds',
        'category': 'Harmful Practices',
        'unit': '%',
        'description': 'Percentage of women who have undergone Female Genital Mutilation'
    },
    'SP.M15.2024.FE.ZS': {
        'name': 'Married by 15',
        'color_scheme': 'reds',
        'category': 'Harmful Practices',
        'unit': '%',
        'description': 'Percentage of women married by age 15'
    },
    'SP.M18.2024.FE.ZS': {
        'name': 'Married by 18',
        'color_scheme': 'oranges',
        'category': 'Harmful Practices',
        'unit': '%',
        'description': 'Percentage of women married by age 18'
    },

    # ============================================================
    # EDUCATION (Greens)
    # ============================================================
    'SE.ENR.ORPH': {
        'name': 'Orphan school attendance ratio',
        'color_scheme': 'greens',
        'category': 'Education',
        'unit': 'ratio',
        'description': 'Ratio of orphan to non-orphan school attendance'
    },

    # ============================================================
    # SOCIAL INCLUSION & BIRTH REGISTRATION (Teals)
    # ============================================================
    'ID.OWN.BRTH.ZS': {
        'name': 'Birth certification',
        'color_scheme': 'teals',
        'category': 'Birth Registration',
        'unit': '%',
        'description': 'Percentage of children with birth certificates'
    },
    'SP.REG.BRTH.RU.ZS': {
        'name': 'Completeness, rural',
        'color_scheme': 'teals',
        'category': 'Birth Registration',
        'unit': '%',
        'description': 'Completeness of birth registration in rural areas'
    },
    'SP.REG.BRTH.UR.ZS': {
        'name': 'Completeness, urban',
        'color_scheme': 'teals',
        'category': 'Birth Registration',
        'unit': '%',
        'description': 'Completeness of birth registration in urban areas'
    },

    # ============================================================
    # EARLY CHILDHOOD DEVELOPMENT (Greens/Oranges)
    # ============================================================
    'SH.STA.BFED.ZS': {
        'name': 'Exclusive breastfeeding',
        'color_scheme': 'greens',
        'category': 'Early Childhood',
        'unit': '%',
        'description': 'Percentage of infants exclusively breastfed for first 6 months'
    },
    'SH.STA.BRTW.ZS': {
        'name': 'Low birthweight',
        'color_scheme': 'oranges',
        'category': 'Early Childhood',
        'unit': '%',
        'description': 'Percentage of newborns with low birthweight (<2.5kg)'
    },
    'SH.STA.OWGH.MA.ZS': {
        'name': 'Overweight, male',
        'color_scheme': 'oranges',
        'category': 'Early Childhood',
        'unit': '%',
        'description': 'Percentage of male children who are overweight'
    },
    'SH.STA.STNT.ZS': {
        'name': 'Stunting',
        'color_scheme': 'oranges',
        'category': 'Early Childhood',
        'unit': '%',
        'description': 'Percentage of children under 5 who are stunted'
    },
    'SH.STA.WAST.ZS': {
        'name': 'Wasting',
        'color_scheme': 'oranges',
        'category': 'Early Childhood',
        'unit': '%',
        'description': 'Percentage of children under 5 who are wasted'
    },
    'HD.HCI.STNT': {
        'name': 'Fraction not stunted',
        'color_scheme': 'greens',
        'category': 'Early Childhood',
        'unit': 'fraction',
        'description': 'Fraction of children not stunted (1 - stunting rate)'
    },
}

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_indicator_name(code):
    """Return human-readable name for indicator code."""
    return INDICATOR_METADATA.get(code, {}).get('name', code)

def get_indicator_metadata(code):
    """Return full metadata for indicator code."""
    return INDICATOR_METADATA.get(code, {
        'name': code,
        'color_scheme': 'blues',
        'category': 'Unknown',
        'unit': '',
        'description': ''
    })

def get_color_scheme(code):
    """Return color scheme for indicator."""
    return INDICATOR_METADATA.get(code, {}).get('color_scheme', 'blues')

def get_indicator_category(code):
    """Return category for indicator."""
    return INDICATOR_METADATA.get(code, {}).get('category', 'Unknown')

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