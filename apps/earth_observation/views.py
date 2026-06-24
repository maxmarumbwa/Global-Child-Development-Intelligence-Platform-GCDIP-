
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



#
########### Old code for rendering raster to png image
##
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

def remote_sensing_view(request):
    """Render the HTML page with the map"""
    return render(request, 'earth_observation/remote_sensing.html')
def view_raster(request):
    """Render the HTML page with the map"""
    return render(request, 'earth_observation/view-raster.html')

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
