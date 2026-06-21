import rasterio
import numpy as np
from PIL import Image

tif_path = r"static\data\raster\baseline_climate_environment\rainfall\wc2.1_10m_prec_01.tif"

png_path = r"static\tiles\rainfall\wc2.1_10m_prec_01.png"

with rasterio.open(tif_path) as src:

    band = src.read(1)

    if src.nodata is not None:
        band = np.ma.masked_equal(band, src.nodata)

    band_min = band.min()
    band_max = band.max()

    normalized = (
        (band - band_min)
        / (band_max - band_min)
        * 255
    )

    img = Image.fromarray(
        normalized.astype(np.uint8)
    )

    img.save(png_path)

print("PNG created:", png_path)