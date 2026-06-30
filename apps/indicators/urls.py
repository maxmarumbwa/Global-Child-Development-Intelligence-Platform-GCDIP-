from django.urls import path
from . import views 

urlpatterns = [
    # Main dynamic view - table is default
    path('indicator/<str:indicator_code>/<str:view_type>/', views.indicator_view, name='indicator_view'),
    path('indicator/<str:indicator_code>/', views.indicator_view, {'view_type': 'table'}, name='indicator_default'),
    
    # API endpoints
    path('api/indicator-data/', views.indicator_data_api, name='indicator_data_api'),
]


############## OLD ############
# from django.urls import path
# from . import views 
# urlpatterns = [

# path('mortality-chart/', views.mortality_chart, name='mortality_chart'),
# path('mortality-chart-year/', views.mortality_chart_year, name='mortality_chart_year'),
# path('mortality-chart-data/', views.mortality_chart_data, name='mortality_chart_data'),
# path('mortality-table/', views.mortality_table, name='mortality_table'),
# path('', views.mortality_map, name='mortality_map'),
# path('mortality-all/', views.mortality_all, name='mortality_all'),
# ]