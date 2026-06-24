import os
import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Convert GeoTIFFs to EPSG:3857 Cloud Optimized GeoTIFFs (COGs)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--input-dir',
            type=str,
            default='static/data/raster/baseline_climate_environment/rainfall/tif',
            help='Directory containing input TIFF files'
        )

        parser.add_argument(
            '--compress',
            type=str,
            default='DEFLATE',
            choices=['DEFLATE', 'LZW', 'ZSTD'],
            help='COG compression type'
        )

    def handle(self, *args, **options):

        input_dir = os.path.join(
            settings.BASE_DIR,
            options['input_dir']
        )

        compress = options['compress']

        if not os.path.exists(input_dir):
            self.stdout.write(
                self.style.ERROR(
                    f'Input directory not found: {input_dir}'
                )
            )
            return

        tif_files = [
            f for f in os.listdir(input_dir)
            if f.lower().endswith('.tif')
            and not f.lower().endswith('_cog.tif')
        ]

        if not tif_files:
            self.stdout.write(
                self.style.WARNING('No TIFF files found.')
            )
            return

        total = len(tif_files)

        self.stdout.write(
            self.style.SUCCESS(
                f'Found {total} TIFF files'
            )
        )

        for i, fname in enumerate(tif_files, start=1):

            src_path = os.path.join(input_dir, fname)

            out_name = fname.replace('.tif', '_cog.tif')
            out_path = os.path.join(input_dir, out_name)

            self.stdout.write(
                f'[{i}/{total}] Processing {fname}'
            )

            cmd = [
                'gdalwarp',
                '-t_srs', 'EPSG:3857',
                '-r', 'bilinear',
                '-multi',
                '-wo', 'NUM_THREADS=ALL_CPUS',
                '-of', 'COG',
                '-co', f'COMPRESS={compress}',
                '-co', 'OVERVIEWS=AUTO',
                '-co', 'BLOCKSIZE=512',
                src_path,
                out_path
            ]

            try:
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created: {out_name}'
                    )
                )

            except subprocess.CalledProcessError as e:

                self.stdout.write(
                    self.style.ERROR(
                        f'Failed: {fname}'
                    )
                )

                self.stdout.write(
                    self.style.ERROR(e.stderr)
                )

        self.stdout.write(
            self.style.SUCCESS(
                'All conversions complete.'
            )
        )