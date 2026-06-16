
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "",
        include("apps.core.urls")
    ),
    path(
        "boundaries/",
        include("apps.boundaries.urls")
    ),
    path(
        "indicators/",
        include("apps.indicators.urls")
    ),

    path(
        "profiles/",
        include("apps.country_profiles.urls")
    ),

    path(
        "trends/",
        include("apps.trends.urls")
    ),

    path(
        "analytics/",
        include("apps.analytics.urls")
    ),

    path(
        "comparison/",
        include("apps.comparison.urls")
    ),

    path(
        "downloads/",
        include("apps.downloads.urls")
    ),

    path(
        "api/",
        include("apps.api.urls")
    ),

]
