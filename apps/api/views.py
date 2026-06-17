from django.shortcuts import render
from django.http import JsonResponse
from .services import get_child_mortality

# =========================================================
# PAGE VIEW (initial load with default year 2023)
# =========================================================

def mortality_chart(request):
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
    df = df.head(150)

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