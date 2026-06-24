
import os
import numpy as np
import rasterio
from PIL import Image
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings

# Directory where your COG files are stored
DATA_DIR = os.path.join(settings.BASE_DIR, 'static', 'rain_cog')
print(f"Looking for COG files in: {DATA_DIR}")
def get_file_path(month):
    """month: int 1..12"""
    if not 1 <= month <= 12:
        raise ValueError("Month must be 1-12")
    return os.path.join(DATA_DIR, f"wc2.1_10m_prec_{month:02d}_cog.tif")

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
