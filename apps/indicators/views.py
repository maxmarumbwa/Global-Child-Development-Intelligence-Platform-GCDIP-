from django.shortcuts import render

from .services import get_child_mortality


# =========================================================
# TABLE VIEW
# =========================================================

def mortality_table(request):

    df = get_child_mortality()

    if df.empty:

        return render(
            request,
            "indicators/mortality.html",
            {
                "records": [],
                "continents": [],
                "income_groups": [],
                "subregions": []
            }
        )

    records = (
        df.sort_values(
            "mortality",
            ascending=False
        ).to_dict(
            orient="records"
        )
    )

    continents = sorted(
        df["continent"]
        .dropna()
        .unique()
        .tolist()
    )

    income_groups = sorted(
        df["income_group"]
        .dropna()
        .unique()
        .tolist()
    )

    subregions = sorted(
        df["subregion"]
        .dropna()
        .unique()
        .tolist()
    )

    return render(
        request,
        "indicators/mortality.html",
        {
            "records": records,
            "continents": continents,
            "income_groups": income_groups,
            "subregions": subregions
        }
    )


# =========================================================
# CHART VIEW
# =========================================================

def mortality_chart(request):

    df = get_child_mortality()

    if df.empty:

        return render(
            request,
            "indicators/mortality_chart.html",
            {
                "records": [],
                "continents": [],
                "income_groups": [],
                "subregions": []
            }
        )

    # limit for performance/testing
    df = df.head(150)

    records = df.to_dict(
        orient="records"
    )

    continents = sorted(
        df["continent"]
        .dropna()
        .unique()
        .tolist()
    )

    income_groups = sorted(
        df["income_group"]
        .dropna()
        .unique()
        .tolist()
    )

    subregions = sorted(
        df["subregion"]
        .dropna()
        .unique()
        .tolist()
    )

    return render(
        request,
        "indicators/mortality_chart.html",
        {
            "records": records,
            "continents": continents,
            "income_groups": income_groups,
            "subregions": subregions
        }
    )