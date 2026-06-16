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