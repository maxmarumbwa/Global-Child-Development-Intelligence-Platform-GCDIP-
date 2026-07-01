from django.shortcuts import render
from django.http import JsonResponse
from .services import (
    fetch_indicator_data, 
    get_indicator_name, 
    get_indicator_metadata,
    get_color_scheme
)
import json

def indicator_view(request, indicator_code='SH.DYN.MORT', view_type='table'):
    """
    Generic view for any indicator with chart, table, or map views.
    Default view is 'table'.
    """
    # Get year from query string, default to 2023
    year = request.GET.get("year")
    try:
        year = int(year) if year else 2023
    except ValueError:
        year = 2023

    # Fetch data for the specific indicator (single API call)
    df = fetch_indicator_data(indicator_code, 1960, 2024)
    
    # Get indicator metadata
    metadata = get_indicator_metadata(indicator_code)
    indicator_name = metadata.get('name', indicator_code)
    color_scheme = metadata.get('color_scheme', 'blues')
    category = metadata.get('category', 'Unknown')
    unit = metadata.get('unit', '')
    description = metadata.get('description', '')
    
    if df.empty:
        return render(request, "indicators/indicator_view.html", {
            "all_data_json": "{}",
            "current_year": 2023,
            "continents": [],
            "income_groups": [],
            "subregions": [],
            "indicator_code": indicator_code,
            "view_type": view_type,
            "indicator_name": indicator_name,
            "color_scheme": color_scheme,
            "category": category,
            "unit": unit,
            "description": description,
        })

    # Build data by year
    data_by_year = {}
    for yr in df['year'].unique():
        year_df = df[df['year'] == yr]
        # For table view, show all data; for others, limit for performance
        if view_type == 'table':
            records = year_df.to_dict(orient='records')
        else:
            records = year_df.head(200).to_dict(orient='records')
        data_by_year[str(yr)] = records

    # Extract filter options
    continents = sorted(df['continent'].dropna().unique().tolist())
    income_groups = sorted(df['income_group'].dropna().unique().tolist())
    subregions = sorted(df['subregion'].dropna().unique().tolist())

    all_data_json = json.dumps(data_by_year)

    return render(request, "indicators/indicator_view.html", {
        "all_data_json": all_data_json,
        "current_year": 2023,
        "continents": continents,
        "income_groups": income_groups,
        "subregions": subregions,
        "indicator_code": indicator_code,
        "view_type": view_type,
        "indicator_name": indicator_name,
        "color_scheme": color_scheme,
        "category": category,
        "unit": unit,
        "description": description,
    })

# =========================================================
# API ENDPOINTS
# =========================================================

def indicator_data_api(request):
    """API endpoint for indicator data."""
    indicator_code = request.GET.get("indicator", "SH.DYN.MORT")
    year = request.GET.get("year")
    
    try:
        year = int(year) if year else 2023
    except ValueError:
        year = 2023

    df = fetch_indicator_data(indicator_code, year, year)
    if df.empty:
        return JsonResponse({"records": [], "continents": [], "income_groups": [], "subregions": []})

    records = df.head(200).to_dict(orient="records")
    continents = sorted(df["continent"].dropna().unique().tolist())
    income_groups = sorted(df["income_group"].dropna().unique().tolist())
    subregions = sorted(df["subregion"].dropna().unique().tolist())

    return JsonResponse({
        "records": records,
        "continents": continents,
        "income_groups": income_groups,
        "subregions": subregions,
        "indicator_code": indicator_code,
    })