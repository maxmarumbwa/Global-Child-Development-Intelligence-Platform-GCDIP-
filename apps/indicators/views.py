from django.shortcuts import render

from .services import (
    get_child_mortality
)


def mortality_table(request):

    df = get_child_mortality()

    records = (
        df
        .sort_values(
            "mortality",
            ascending=False
        )
        .to_dict(
            orient="records"
        )
    )

    return render(
        request,
        "indicators/mortality.html",
        {
            "records": records
        }
    )
    
def mortality_chart(request):

    df = get_child_mortality()

    # optional for testing
    df = df.head(150)

    records = df.to_dict(
        orient="records"
    )

    return render(
        request,
        "indicators/mortality_chart.html",
        {
            "records": records
        }
    )