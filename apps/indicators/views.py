from django.shortcuts import render
from django.http import JsonResponse
from .services import (
    get_indicator_data_range, 
    get_indicator_data,
    get_child_mortality_range,
    get_child_mortality,
    get_indicator_name
)
import json

# =========================================================
# MAIN VIEW WITH INDICATOR PARAMETER
# =========================================================

def indicator_view(request, indicator_code='SH.DYN.MORT', view_type='chart'):
    """
    Generic view for any indicator with chart, table, or map views.
    
    Args:
        indicator_code: World Bank indicator code (e.g., 'SH.DYN.MORT')
        view_type: 'chart', 'table', or 'map'
    """
    # Get year from query string, default to 2023
    year = request.GET.get("year")
    try:
        year = int(year) if year else 2023
    except ValueError:
        year = 2023

    # Fetch data for the specific indicator
    df = get_indicator_data_range(indicator_code, 1960, 2024)
    
    if df.empty:
        return render(request, "indicators/indicator_view.html", {
            "all_data_json": "{}",
            "current_year": 2023,
            "continents": [],
            "income_groups": [],
            "subregions": [],
            "indicator_code": indicator_code,
            "view_type": view_type,
            "indicator_name": get_indicator_name(indicator_code),
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
        "indicator_name": get_indicator_name(indicator_code),
    })

# =========================================================
# BACKWARD COMPATIBILITY VIEWS
# =========================================================

def mortality_chart(request):
    """Redirect to generic view with chart type."""
    return indicator_view(request, 'SH.DYN.MORT', 'chart')

def mortality_table(request):
    """Redirect to generic view with table type."""
    return indicator_view(request, 'SH.DYN.MORT', 'table')

def mortality_map(request):
    """Redirect to generic view with map type."""
    return indicator_view(request, 'SH.DYN.MORT', 'map')

def mortality_all(request):
    """Redirect to generic view with all views."""
    return render_combined_view(request, 'SH.DYN.MORT')

def render_combined_view(request, indicator_code):
    """Render combined chart, table, and map view."""
    df = get_indicator_data_range(indicator_code, 1960, 2024)
    if df.empty:
        return render(request, "indicators/mortality_all.html", {
            "all_data_json": "{}",
            "current_year": 2023,
            "continents": [],
            "income_groups": [],
            "subregions": [],
            "indicator_code": indicator_code,
            "indicator_name": get_indicator_name(indicator_code),
        })

    data_by_year = {}
    for yr in df['year'].unique():
        year_df = df[df['year'] == yr]
        records = year_df.head(200).to_dict(orient='records')
        data_by_year[str(yr)] = records

    continents = sorted(df['continent'].dropna().unique().tolist())
    income_groups = sorted(df['income_group'].dropna().unique().tolist())
    subregions = sorted(df['subregion'].dropna().unique().tolist())

    all_data_json = json.dumps(data_by_year)

    return render(request, "indicators/mortality_all.html", {
        "all_data_json": all_data_json,
        "current_year": 2023,
        "continents": continents,
        "income_groups": income_groups,
        "subregions": subregions,
        "indicator_code": indicator_code,
        "indicator_name": get_indicator_name(indicator_code),
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

    df = get_indicator_data(indicator_code, year)
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