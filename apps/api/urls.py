from django.urls import path
from . import views 
urlpatterns = [

path('mortality-chart_api/', views.mortality_chart_api, name='mortality_chart_api'),
path('mortality-chart-data/', views.mortality_chart_data, name='mortality_chart_data'),

]