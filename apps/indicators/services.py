import requests
import pandas as pd


def get_child_mortality():

    url = (
        "https://api.worldbank.org/v2/"
        "country/all/"
        "indicator/SH.DYN.MORT"
        "?format=json"
        "&per_page=20000"
        "&date=2023:2023"
    )

    response = requests.get(url)

    data = response.json()[1]

    rows = []

    for row in data:

        if row["value"] is None:
            continue

        rows.append({

            "iso3":
                row["countryiso3code"],

            "country":
                row["country"]["value"],

            "year":
                row["date"],

            "mortality":
                row["value"]

        })

    return pd.DataFrame(rows)