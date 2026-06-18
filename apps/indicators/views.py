from django.shortcuts import render
from django.http import JsonResponse
from .services import get_child_mortality, get_child_mortality_range
import json

# =========================================================
# PAGE VIEW (initial load with default year 2023)
# =========================================================

def mortality_chart_year(request):
    # Get year from query string, default to 2023
    year = request.GET.get("year")
    try:
        year = int(year) if year else 2023
    except ValueError:
        year = 2023

    df = get_child_mortality(year)

    if df.empty:
        return render(
            request,
            "indicators/mortality_chart.html",
            {
                "records": [],
                "continents": [],
                "income_groups": [],
                "subregions": [],
                "current_year": year,
            }
        )

    # Limit for performance (optional)
    # df = df.head(150)

    records = df.to_dict(orient="records")
    continents = sorted(df["continent"].dropna().unique().tolist())
    income_groups = sorted(df["income_group"].dropna().unique().tolist())
    subregions = sorted(df["subregion"].dropna().unique().tolist())

    return render(
        request,
        "indicators/mortality_chart.html",
        {
            "records": records,
            "continents": continents,
            "income_groups": income_groups,
            "subregions": subregions,
            "current_year": year,
        }
    )

def mortality_chart(request):
    # Fetch all years data once
    df = get_child_mortality_range(1960, 2024)
    if df.empty:
        return render(request, "indicators/mortality_chart.html", {
            "all_data_json": "{}",
            "current_year": 2023
        })

    # Build data by year, limit to top 150 per year
    data_by_year = {}
    for year in df['year'].unique():
        year_df = df[df['year'] == year].head(150)
        records = year_df.to_dict(orient='records')
        data_by_year[str(year)] = records

    # Also extract all distinct continents, income_groups, subregions for filters
    continents = sorted(df['continent'].dropna().unique().tolist())
    income_groups = sorted(df['income_group'].dropna().unique().tolist())
    subregions = sorted(df['subregion'].dropna().unique().tolist())

    import json
    all_data_json = json.dumps(data_by_year)

    return render(request, "indicators/mortality_chart.html", {
        "all_data_json": all_data_json,
        "current_year": 2023,
        "continents": continents,
        "income_groups": income_groups,
        "subregions": subregions,
    })
# =========================================================
# JSON DATA ENDPOINT (for AJAX year updates)
# =========================================================

def mortality_chart_data(request):
    year = request.GET.get("year")
    try:
        year = int(year) if year else 2023
    except ValueError:
        year = 2023

    df = get_child_mortality(year)
    if df.empty:
        return JsonResponse({"records": [], "continents": [], "income_groups": [], "subregions": []})

    df = df.head(150)
    records = df.to_dict(orient="records")
    continents = sorted(df["continent"].dropna().unique().tolist())
    income_groups = sorted(df["income_group"].dropna().unique().tolist())
    subregions = sorted(df["subregion"].dropna().unique().tolist())

    return JsonResponse({
        "records": records,
        "continents": continents,
        "income_groups": income_groups,
        "subregions": subregions,
    })
    

# new view to show all data
def mortality_chart_all_data(request):
    df = get_child_mortality_range(1960, 2024)
    if df.empty:
        return JsonResponse({"data": {}})
    # Group by year
    data_by_year = {}
    for year in df['year'].unique():
        year_df = df[df['year'] == year].head(150)  # limit per year
        records = year_df.to_dict(orient='records')
        data_by_year[str(year)] = records
    return JsonResponse({"data": data_by_year})

#
######### Mortality Table View (for all years, no limit) #########
#
def mortality_table(request):
    """
    Render a table view for child mortality data.
    """
    df = get_child_mortality_range(1960, 2024)
    if df.empty:
        return render(request, "indicators/mortality_table.html", {
            "all_data_json": "{}",
            "current_year": 2023,
            "continents": [],
            "income_groups": [],
            "subregions": [],
        })

    # Group data by year
    data_by_year = {}
    for year in df['year'].unique():
        year_df = df[df['year'] == year]  # No limit for table, show all
        records = year_df.to_dict(orient='records')
        data_by_year[str(year)] = records

    # Extract filter options
    continents = sorted(df['continent'].dropna().unique().tolist())
    income_groups = sorted(df['income_group'].dropna().unique().tolist())
    subregions = sorted(df['subregion'].dropna().unique().tolist())

    all_data_json = json.dumps(data_by_year)

    return render(request, "indicators/mortality_table.html", {
        "all_data_json": all_data_json,
        "current_year": 2023,
        "continents": continents,
        "income_groups": income_groups,
        "subregions": subregions,
    })


# View for maplayout
def mortality_map(request):
    """
    Render a choropleth map for child mortality data.
    """
    df = get_child_mortality_range(1960, 2024)
    if df.empty:
        return render(request, "indicators/mortality_map.html", {
            "all_data_json": "{}",
            "current_year": 2023,
            "continents": [],
            "income_groups": [],
            "subregions": [],
        })

    # Group data by year (same as table view)
    data_by_year = {}
    for year in df['year'].unique():
        year_df = df[df['year'] == year]   # all rows
        records = year_df.to_dict(orient='records')
        data_by_year[str(year)] = records

    continents = sorted(df['continent'].dropna().unique().tolist())
    income_groups = sorted(df['income_group'].dropna().unique().tolist())
    subregions = sorted(df['subregion'].dropna().unique().tolist())

    import json
    all_data_json = json.dumps(data_by_year)

    return render(request, "indicators/mortality_map.html", {
        "all_data_json": all_data_json,
        "current_year": 2023,
        "continents": continents,
        "income_groups": income_groups,
        "subregions": subregions,
    })
    
    