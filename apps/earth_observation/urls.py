from django.urls import path
from . import views

urlpatterns = [
    path('', views.remote_sensing_view, name='remote_sensing'),
    path('api/classified/<int:month>/', views.monthly_lta_classified, name='classified'),
    path('api/metadata/<int:month>/', views.monthly_lta_metadata, name='metadata'),
]