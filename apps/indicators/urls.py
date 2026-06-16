from django.urls import path
from .views import mortality_table

urlpatterns = [

    path(
        "mortality/",
        mortality_table,
        name="mortality_table"
    ),

]