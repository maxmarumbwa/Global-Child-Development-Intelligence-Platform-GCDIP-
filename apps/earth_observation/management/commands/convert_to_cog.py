import os
import rasterio
from rasterio.shutil import copy as rio_copy
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Convert GeoTIFFs to Cloud Optimized GeoTIFFs (COG)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input-dir',
            type=str,
            default='static/data/raster/baseline_climate_environment/rainfall',
            help='Input directory containing .tif files'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='static/data/raster/baseline_climate_environment/rainfall/cog',
            help='Output directory for COG files'
        )
        parser.add_argument(
            '--compress',
            type=str,
            default='deflate',
            choices=['deflate', 'lzw', 'packbits', 'zstd'],
            help='Compression algorithm'
        )

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        input_dir = os.path.join(base_dir, options['input_dir'])
        output_dir = os.path.join(base_dir, options['output_dir'])
        compress = options['compress']

        if not os.path.exists(input_dir):
            self.stdout.write(self.style.ERROR(f'Input directory not found: {input_dir}'))
            return

        os.makedirs(output_dir, exist_ok=True)

        for fname in os.listdir(input_dir):
            if not fname.endswith('.tif') or '_cog' in fname:
                continue

            src_path = os.path.join(input_dir, fname)
            cog_name = fname.replace('.tif', '_cog.tif')
            cog_path = os.path.join(output_dir, cog_name)

            self.stdout.write(f'Converting {fname} ...')

            try:
                with rasterio.open(src_path) as src:
                    profile = src.profile.copy()
                    profile.update(
                        driver='GTiff',
                        tiled=True,
                        blockxsize=512,
                        blockysize=512,
                        compress=compress,
                        interleave='band',
                    )
                    rio_copy(src, cog_path, **profile, copy_src_overviews=True)
                    self.stdout.write(self.style.SUCCESS(f'COG created: {cog_path}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to convert {fname}: {e}'))

        self.stdout.write(self.style.SUCCESS('All conversions complete.'))