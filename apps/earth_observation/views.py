
# views.py

import io
import numpy as np
import rasterio
from PIL import Image
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from .config import DATA_ROOT, DATASET_REGISTRY

def raster_classified_view(request, dataset, month=None):
    """
    Handles both:
    - Static: /raster/demographics/
    - Monthly: /raster/temperature/3/
    """
    try:
        config = DATASET_REGISTRY.get(dataset)
        if not config:
            return JsonResponse({'error': f'Unknown dataset: {dataset}'}, status=404)

        # 1. Validate parameters based on config
        required_params = config['params']
        param_values = {}

        if 'month' in required_params:
            if month is None:
                return JsonResponse({'error': 'Month parameter is required for this dataset'}, status=400)
            try:
                month_int = int(month)
                if not (1 <= month_int <= 12):
                    raise ValueError
                param_values['month'] = month_int
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Month must be an integer between 1 and 12'}, status=400)
        else:
            # If dataset is static, ignore 'month' even if accidentally passed
            if month is not None:
                # You could log a warning, but we'll just ignore it
                pass

        # 2. Build the file path
        filename = config['file_pattern'].format(**param_values)
        file_path = os.path.join(DATA_ROOT, config['folder'], filename)

        if not os.path.exists(file_path):
            return JsonResponse({'error': f'File not found: {filename}'}, status=404)

        # 3. Read raster
        with rasterio.open(file_path) as src:
            data = src.read(1).astype('float32')
            nodata = src.nodata
            if nodata is not None:
                data[data == nodata] = np.nan

        # 4. Classify
        rgb_array = config['classify'](data)

        # 5. Return PNG
        buf = io.BytesIO()
        Image.fromarray(rgb_array).save(buf, 'PNG')
        buf.seek(0)
        return FileResponse(buf, content_type='image/png')

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

### Metatdata view for monthly datasets
def raster_metadata_view(request, dataset, month=None):
    config = DATASET_REGISTRY.get(dataset)
    if not config:
        return JsonResponse({'error': 'Unknown dataset'}, status=404)

    # Build path (same logic as above)
    param_values = {}
    if 'month' in config['params']:
        if month is None:
            return JsonResponse({'error': 'Month required'}, status=400)
        param_values['month'] = int(month)
    
    filename = config['file_pattern'].format(**param_values)
    file_path = os.path.join(DATA_ROOT, config['folder'], filename)

    if not os.path.exists(file_path):
        return JsonResponse({'error': 'File not found'}, status=404)

    with rasterio.open(file_path) as src:
        bounds = src.bounds
        return JsonResponse({
            'bounds': {
                'west': bounds.left,
                'south': bounds.bottom,
                'east': bounds.right,
                'north': bounds.top,
            },
            'width': src.width,
            'height': src.height,
            'crs': str(src.crs),
        })

############# Views for rendering HTML pages ###########
def test(request):
    """Render the HTML page with the map"""
    return render(request, 'earth_observation/test.html')
def remote_sensing_view(request):
    """Render the HTML page with the map"""
    return render(request, 'earth_observation/remote_sensing.html')
def view_raster(request):
    """Render the HTML page with the map"""
    return render(request, 'earth_observation/view-raster.html')






###########################################################################################
#
# ################################ DATA ANALYSIS VIEWS ######################\
    
###########################################################################################
    
############################ Get pixel location from raster ################
import os
import math
import numpy as np
import rasterio
from django.http import JsonResponse
from .config import DATA_ROOT, DATASET_REGISTRY

def lonlat_to_webmercator(lon, lat):
    """Convert EPSG:4326 lon/lat to EPSG:3857 meters."""
    x = lon * 20037508.34 / 180.0
    y = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    y = y * 20037508.34 / 180.0
    return x, y

def raster_point_query(request, dataset, month=None):
    try:
        config = DATASET_REGISTRY.get(dataset)
        if not config:
            return JsonResponse({'error': 'Unknown dataset'}, status=404)

        lat = float(request.GET.get('lat', 0))
        lon = float(request.GET.get('lon', 0))

        param_values = {}
        if 'month' in config.get('params', []):
            if month is None:
                return JsonResponse({'error': 'Month required'}, status=400)
            param_values['month'] = int(month)

        filename = config['file_pattern'].format(**param_values)
        file_path = os.path.join(DATA_ROOT, config['folder'], filename)

        if not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found'}, status=404)

        # Convert lat/lon to EPSG:3857
        x, y = lonlat_to_webmercator(lon, lat)

        with rasterio.open(file_path) as src:
            row, col = src.index(x, y)

            if row < 0 or row >= src.height or col < 0 or col >= src.width:
                return JsonResponse({'error': 'Point outside raster'}, status=400)

            value = src.read(1)[row, col]

            # Handle nodata and convert numpy type to Python float
            if src.nodata is not None and value == src.nodata:
                value = None
            else:
                value = float(value)  # Convert numpy int16/float32 to Python float

            return JsonResponse({
                'value': value,
                'lat': lat,
                'lon': lon
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
   
   
# country zonal statistics view
import os
import json
import math
import numpy as np
import rasterio
from rasterio.mask import mask
from django.http import JsonResponse
from django.conf import settings
from .config import DATA_ROOT, DATASET_REGISTRY

def lonlat_to_webmercator(lon, lat):
    """Convert EPSG:4326 lon/lat to EPSG:3857 meters."""
    x = lon * 20037508.34 / 180.0
    y = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    y = y * 20037508.34 / 180.0
    return x, y

def transform_geom_to_3857(geom):
    """
    Recursively transform a GeoJSON geometry from EPSG:4326 to EPSG:3857.
    Works for Point, LineString, Polygon, MultiPolygon, etc.
    """
    geom_type = geom['type']
    if geom_type == 'Point':
        x, y = lonlat_to_webmercator(geom['coordinates'][0], geom['coordinates'][1])
        return {'type': 'Point', 'coordinates': [x, y]}
    elif geom_type in ['LineString', 'MultiPoint']:
        new_coords = [lonlat_to_webmercator(c[0], c[1]) for c in geom['coordinates']]
        return {'type': geom_type, 'coordinates': new_coords}
    elif geom_type == 'Polygon':
        new_coords = []
        for ring in geom['coordinates']:
            new_ring = [lonlat_to_webmercator(c[0], c[1]) for c in ring]
            new_coords.append(new_ring)
        return {'type': 'Polygon', 'coordinates': new_coords}
    elif geom_type == 'MultiPolygon':
        new_coords = []
        for poly in geom['coordinates']:
            new_poly = []
            for ring in poly:
                new_ring = [lonlat_to_webmercator(c[0], c[1]) for c in ring]
                new_poly.append(new_ring)
            new_coords.append(new_poly)
        return {'type': 'MultiPolygon', 'coordinates': new_coords}
    else:
        # Fallback for other types (e.g., GeometryCollection)
        return geom

def zonal_stats_view(request, dataset, month=None):
    try:
        config = DATASET_REGISTRY.get(dataset)
        if not config:
            return JsonResponse({'error': 'Unknown dataset'}, status=404)

        country_name = request.GET.get('country')
        if not country_name:
            return JsonResponse({'error': 'Missing country parameter'}, status=400)

        # 1. Load countries GeoJSON
        geojson_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'geojson', 'ne_10m_admin_0_countries_sm.geojson')
        if not os.path.exists(geojson_path):
            return JsonResponse({'error': 'Countries GeoJSON not found'}, status=404)

        with open(geojson_path, encoding='utf-8') as f:
            countries = json.load(f)

        # Find the feature with matching NAME_EN
        feature = None
        for feat in countries['features']:
            if feat['properties'].get('NAME_EN') == country_name:
                feature = feat
                break
        if not feature:
            return JsonResponse({'error': f'Country "{country_name}" not found'}, status=404)

        # 2. Build raster file path
        param_values = {}
        if 'month' in config.get('params', []):
            if month is None:
                return JsonResponse({'error': 'Month required for this dataset'}, status=400)
            param_values['month'] = int(month)
        filename = config['file_pattern'].format(**param_values)
        file_path = os.path.join(DATA_ROOT, config['folder'], filename)

        if not os.path.exists(file_path):
            return JsonResponse({'error': f'Raster file not found: {filename}'}, status=404)

        # 3. Transform geometry to EPSG:3857 (manual, no PROJ)
        geom_3857 = transform_geom_to_3857(feature['geometry'])

        # 4. Open raster and mask with transformed geometry
        with rasterio.open(file_path) as src:
            # Since we transformed to EPSG:3857 and the raster is also EPSG:3857,
            # we can pass the geometry directly without further reprojection.
            out_image, out_transform = mask(src, [geom_3857], crop=True)
            data = out_image[0]  # first band

            # Handle nodata
            nodata = src.nodata
            if nodata is not None:
                data = np.where(data == nodata, np.nan, data)

            # Flatten and remove nan
            flat = data.flatten()
            valid = flat[~np.isnan(flat)]

            if len(valid) == 0:
                return JsonResponse({'error': 'No valid pixels in the country'}, status=400)

            stats = {
                'mean': float(np.mean(valid)),
                'min': float(np.min(valid)),
                'max': float(np.max(valid)),
                'sum': float(np.sum(valid)),
                'count': int(len(valid)),
                'std': float(np.std(valid)),
            }
            return JsonResponse(stats)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
 
####################################################################################
#####################################################################################
########### Old code for rendering raster to png image
######################################################################################
####################################################################################
import io
import os
import numpy as np
import rasterio
from PIL import Image
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings

# Directory where your COG files are stored
DATA_DIR2 = os.path.join(settings.BASE_DIR, 'static', 'rain_cog')
print(f"Looking for COG files in: {DATA_DIR2}")
def get_file_path(month):
    """month: int 1..12"""
    if not 1 <= month <= 12:
        raise ValueError("Month must be 1-12")
    return os.path.join(DATA_DIR2, f"wc2.1_10m_prec_{month:02d}_cog.tif")


def rain_classified(request, month):
    """
    Return a classified PNG image overlay for the given month.
    """
    try:
        month = int(month)
        file_path = get_file_path(month)
        if not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found'}, status=404)

        with rasterio.open(file_path) as src:
            data = src.read(1).astype('float32')
            nodata = src.nodata
            if nodata is not None:
                data[data == nodata] = np.nan

        # Classify into 4 classes (mm)
        out = np.zeros((*data.shape, 3), dtype=np.uint8)
        out[np.isnan(data)] = (255, 255, 255)                      # NoData
        out[(data >= 0) & (data <= 25)] = (222, 235, 247)       # Very Low
        out[(data > 25) & (data <= 75)] = (158, 202, 225)       # Low
        out[(data > 75) & (data <= 150)] = (49, 130, 189)       # Moderate
        out[(data > 150)] = (8, 48, 107)                        # High              

        buf = io.BytesIO()
        Image.fromarray(out).save(buf, 'PNG')
        buf.seek(0)
        return FileResponse(buf, content_type='image/png')

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def rainfall_metadata(request, month):
    """Return bounds and basic info for a given month"""
    try:
        month = int(month)
        file_path = get_file_path(month)
        if not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found'}, status=404)
        with rasterio.open(file_path) as src:
            bounds = src.bounds  # (left, bottom, right, top)
            metadata = {
                'bounds': {
                    'west': bounds.left,
                    'south': bounds.bottom,
                    'east': bounds.right,
                    'north': bounds.top,
                },
                'width': src.width,
                'height': src.height,
                'crs': str(src.crs),
            }
        return JsonResponse(metadata)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
