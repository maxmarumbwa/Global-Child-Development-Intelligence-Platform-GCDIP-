from django.urls import path
from .views import mortality_table, mortality_chart

urlpatterns = [

    path(
        "mortality/",
        mortality_table,
        name="mortality_table"
    ),

    path(
        "mortality/chart/",
        mortality_chart,
        name="mortality_chart"
    ),

]