# config.py

import os
import numpy as np
from django.conf import settings

DATA_ROOT = os.path.join(settings.BASE_DIR, 'static', 'data', 'cog')

# ---------- Classification Functions (Static & Temporal) ----------

def classify_precipitation(data):
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data >= 0) & (data <= 25)]   = (222, 235, 247)
    out[(data > 25) & (data <= 75)]   = (158, 202, 225)
    out[(data > 75) & (data <= 150)]  = (49, 130, 189)
    out[(data > 150)]                 = (8, 48, 107)
    return out

def classify_temperature(data):
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data < -10)] = (103, 0, 31)
    out[(data >= -10) & (data < 0)]   = (178, 24, 43)
    out[(data >= 0) & (data < 10)]    = (214, 96, 77)
    out[(data >= 10) & (data < 20)]   = (244, 165, 130)
    out[(data >= 20)]                 = (253, 219, 199)
    return out

def classify_demographics(data):
    """Population density (people/km²)"""
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data < 10)] = (237, 248, 233)
    out[(data >= 10) & (data < 50)]  = (199, 233, 180)
    out[(data >= 50) & (data < 200)] = (127, 205, 187)
    out[(data >= 200) & (data < 500)] = (65, 182, 196)
    out[(data >= 500)] = (29, 145, 192)
    return out

def classify_wind_speed(data):
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data < 10)] = (237, 248, 233)
    out[(data >= 10) & (data < 50)]  = (199, 233, 180)
    out[(data >= 50) & (data < 200)] = (127, 205, 187)
    out[(data >= 200) & (data < 500)] = (65, 182, 196)
    out[(data >= 500)] = (29, 145, 192)
    return out

def classify_land_degradation(data):
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data < 10)] = (237, 248, 233)
    out[(data >= 10) & (data < 50)]  = (199, 233, 180)
    out[(data >= 50) & (data < 200)] = (127, 205, 187)
    out[(data >= 200) & (data < 500)] = (65, 182, 196)
    out[(data >= 500)] = (29, 145, 192)
    return out

def classify_flood_risk(data):
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data < 20)] = (254, 224, 139)
    out[(data >= 20) & (data < 40)] = (253, 174, 97)
    out[(data >= 40) & (data < 60)] = (244, 109, 67)
    out[(data >= 60) & (data < 80)] = (213, 62, 79)
    out[(data >= 80)] = (158, 1, 66)
    return out

def classify_drought_risk(data):
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data < 10)] = (237, 248, 233)
    out[(data >= 10) & (data < 50)]  = (199, 233, 180)
    out[(data >= 50) & (data < 200)] = (127, 205, 187)
    out[(data >= 200) & (data < 500)] = (65, 182, 196)
    out[(data >= 500)] = (29, 145, 192)
    return out

def classify_pollution(data):
    """Generic hazard severity (e.g., flood risk, pollution)"""
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data < 0.2)] = (255, 255, 204)
    out[(data >= 0.2) & (data < 0.4)] = (255, 237, 160)
    out[(data >= 0.4) & (data < 0.6)] = (254, 196, 79)
    out[(data >= 0.6) & (data < 0.8)] = (254, 153, 41)
    out[(data >= 0.8)] = (217, 95, 14)
    return out

def classify_diseases (data):
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data < 0.2)] = (255, 255, 204)
    out[(data >= 0.2) & (data < 0.4)] = (255, 237, 160)
    out[(data >= 0.4) & (data < 0.6)] = (254, 196, 79)
    out[(data >= 0.6) & (data < 0.8)] = (254, 153, 41)
    out[(data >= 0.8)] = (217, 95, 14)
    return out

def classify_cyclone(data):
    out = np.zeros((*data.shape, 3), dtype=np.uint8)
    out[np.isnan(data)] = (255, 255, 255)
    out[(data < 10)] = (237, 248, 233)
    out[(data >= 10) & (data < 50)] = (199, 233, 180)
    out[(data >= 50) & (data < 200)] = (127, 205, 187)
    out[(data >= 200) & (data < 500)] = (65, 182, 196)
    out[(data >= 500)] = (29, 145, 192)
    return out

# ---------- Master Registry ----------
DATASET_REGISTRY = {
    
    # --- TEMPORAL DATASETS (params=['month']) ---
    'rainfall': {
        'folder': 'baseline_climate_environment/rainfall',
        'file_pattern': 'wc2.1_10m_prec_{month:02d}_cog.tif',
        'classify': classify_precipitation,
        'params': ['month'],
    },
    'temperature_avg': {
        'folder': 'baseline_climate_environment/temperature/tavg',
        'file_pattern': 'wc2.1_10m_tavg_{month:02d}_cog.tif',
        'classify': classify_temperature,
        'params': ['month'],
    },
    'temperature_min': {
        'folder': 'baseline_climate_environment/temperature/tmin',
        'file_pattern': 'wc2.1_10m_tmin_{month:02d}_cog.tif',
        'classify': classify_temperature,
        'params': ['month'],
    },
    'temperature_max': {
        'folder': 'baseline_climate_environment/temperature/tmax',
        'file_pattern': 'wc2.1_10m_tmax_{month:02d}_cog.tif',
        'classify': classify_temperature,
        'params': ['month'],
    },
    'wind_speed': {
        'folder': 'natural_hazards/wind',
        'file_pattern': 'wc2.1_10m_wind_{month:02d}.tif',
        'classify': classify_wind_speed,  
        'params': ['month'],
    },
        # --- STATIC DATASETS (params=[]) ---
    'demographics_children_female': {
        'folder': 'demographics',
        'file_pattern': 'pop_children_female.tif',   # exact filename
        'classify': classify_demographics,
        'params': [],  # No URL parameters needed
    },
    'demographics_children_male': {
        'folder': 'demographics',
        'file_pattern': 'pop_children_male.tif',   # exact filename
        'classify': classify_demographics,
        'params': [],  # No URL parameters needed
    },
    'demographics_children': {
        'folder': 'demographics',
        'file_pattern': 'pop_children.tif',   # exact filename
        'classify': classify_demographics,
        'params': [],  # No URL parameters needed
    },
    'land_degradation': {
        'folder': 'land',
        'file_pattern': 'land_degradation.tif',
        'classify': classify_land_degradation,   # reuse or define new
        'params': [],
    },
    'flood_risk_coastal': {
        'folder': 'natural_hazards/floods/coastal',
        'file_pattern': 'inuncoast_historical_nosub_hist_rp0500_0.tif',
        #'file_pattern':rp0100_0 rp0500_0 etc
        'classify': classify_flood_risk,   # reuse or define new
        'params': [],
    },
    'flood_risk_fluvial': {
        'folder': 'natural_hazards/floods/inland',
        'file_pattern': 'inunriver_historical_nosub_hist_rp0100_0.tif',
        #'file_pattern':rp0100_0 rp0500_0 etc
        'classify': classify_flood_risk,   # reuse or define new
        'params': [],
    },
    # 'flood_risk_coastal_param': {
    #     'folder': 'natural_hazards/floods/coastal/raster/tif',  # adjust as needed
    #     'file_pattern': 'inuncoast_historical_nosub_hist_rp{rp}_0.tif',  # rp is string
    #     'classify': classify_flood_risk,
    #     'params': ['rp'],
    #     'valid_options': {
    #         'rp': ['0002', '0005', '0010', '0025', '0050', '0100', '0250', '0500', '1000']
    #     }
    # },
    # 'flood_risk_fluvial_param': {
    #     'folder': 'natural_hazards/floods/fluvial/raster/tif',
    #     'file_pattern': 'inunriver_historical_nosub_hist_rp{rp}_0.tif',   # example pattern
    #     'classify': classify_flood_risk,
    #     'params': ['rp'],
    #     'valid_options': {'rp': ['0002', '0005', '0010', '0025', '0050', '0100', '0250', '0500', '1000']}
    # },
    
    'drought_risk': {
        'folder': 'natural_hazards/drought',
        'file_pattern': 'drought_risk.tif',
        'classify': classify_drought_risk,   # reuse or define new
        'params': [],
    },
    'pollution_air': {
        'folder': 'pollution_hazards/air',
        'file_pattern': 'pollution_air.tif',
        'classify': classify_pollution,
        'params': [],
    },
    'pollution_water': {
        'folder': 'pollution_hazards/water',
        'file_pattern': 'pollution_water.tif',
        'classify': classify_pollution,
        'params': [],
    },
    'cyclone_risk': {
        'folder': 'natural_hazards/cyclones',
        'file_pattern': 'cyclones_cat.tif',
        'classify': classify_cyclone,
        'params': [],
    },
    'diseases_cholera': {
        'folder': 'diseases',
        'file_pattern': 'cholera_risk.tif',
        'classify': classify_diseases,
        'params': [],
    },
    'diseases_malaria': {
        'folder': 'diseases',
        'file_pattern': 'malaria_risk.tif',
        'classify': classify_diseases,
        'params': [],
    },

    # ... add 'imgse' or others as needed
}