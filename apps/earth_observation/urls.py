from django.urls import path
from . import views

urlpatterns = [
    path('', views.remote_sensing_view, name='remote_sensing'),
    path('test/', views.test, name='test'),
    path('view-raster/', views.view_raster, name='view_raster'),
    path('api/classified/<int:month>/', views.rain_classified, name='classified'),
    path('api/metadata/<int:month>/', views.rainfall_metadata, name='metadata'),
    ##Dynamic view
    # Static datasets: /raster/demographics/
    path('raster/<str:dataset>/', views.raster_classified_view, name='raster_static'),
    
    # Monthly datasets: /raster/temperature/3/
    path('raster/<str:dataset>/<int:month>/', views.raster_classified_view, name='raster_monthly'),

    # Metadata (same patterns)
    path('metadata/<str:dataset>/', views.raster_metadata_view, name='metadata_static'),
    path('metadata/<str:dataset>/<int:month>/', views.raster_metadata_view, name='metadata_monthly'),
    #
    ######### Data analysis views #############
    path('api/point/<str:dataset>/', views.raster_point_query, name='point_query_static'),
    path('api/point/<str:dataset>/<int:month>/', views.raster_point_query, name='point_query_monthly'),
    
    path('api/zonal_stats/<str:dataset>/', views.zonal_stats_view, name='zonal_stats_static'),
    path('api/zonal_stats/<str:dataset>/<int:month>/', views.zonal_stats_view, name='zonal_stats_monthly'),
    
    
    
]
