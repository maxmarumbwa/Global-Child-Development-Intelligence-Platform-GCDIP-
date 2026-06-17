from django.urls import path
from . import views 
urlpatterns = [

path('mortality-chart/', views.mortality_chart, name='mortality_chart'),
path('mortality-chart-data/', views.mortality_chart_data, name='mortality_chart_data'),

]