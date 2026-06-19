from django.urls import path
from . import views 
urlpatterns = [

path('mortality-chart/', views.mortality_chart, name='mortality_chart'),
path('mortality-chart-year/', views.mortality_chart_year, name='mortality_chart_year'),
path('mortality-chart-data/', views.mortality_chart_data, name='mortality_chart_data'),
path('mortality-table/', views.mortality_table, name='mortality_table'),
path('mortality-map/', views.mortality_map, name='mortality_map'),
path('mortality-all/', views.mortality_all, name='mortality_all'),
]