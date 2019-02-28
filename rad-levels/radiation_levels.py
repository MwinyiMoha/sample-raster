import datetime
import os
import time
import rasterio
from geopandas import GeoDataFrame as GDF
from shapely.geometry import Point
from pyproj import Proj


class RadiationLevels:

    def __init__(self, **args_dict):
        """Initialize tool parameters"""

        self.data_dir = args_dict['data_dir']
        self.vector_file = args_dict['vector']
        self.raster_file = args_dict['raster']
        self.epsg_code = args_dict['epsg']
        self.output_file = args_dict['out_file_prefix']
        self.output_file_type = args_dict['out_file_type']
        self.input_crs = ''

    @staticmethod
    def print_initial():
        """Tool short intro"""

        print('********************************************************')
        print('Tool: Rad Levels')
        print('Author: Mohammed Mwijaa--https://github.com/mwinyimoha')
        print('License: MIT')
        print('********************************************************')

    @staticmethod
    def stamp_print(string):
        """Print method with timestamp"""

        timestamp = datetime.datetime.now()
        formatted = '{}: {}'.format(timestamp, string)
        print(formatted)

    def config_data_dir(self):
        """Configure data directory path"""

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, self.data_dir)
        if not os.path.exists(data_dir):
            self.stamp_print('Data directory not found!!')
            self.stamp_print('Creating data directory...')

            try:
                os.mkdir(data_dir)

                self.stamp_print('Successfully created: {}'.format(data_dir))
                self.stamp_print('Please copy data files to the created directory')
                self.stamp_print('Tool will exit in 3 Seconds...')

                time.sleep(3)
                exit()
            except OSError, e:
                raise e
        else:
            self.data_dir = data_dir
            self.stamp_print('Successfully configured data directory...')

    def config_data_file(self, filename, file_type='raster'):
        """Configure an input file"""

        input_file = os.path.join(self.data_dir, filename)
        if not os.path.exists(input_file):
            self.stamp_print('Specified {} file not found'.format(file_type))
            return False
        else:
            if file_type == 'vector':
                self.vector_file = input_file
            else:
                self.raster_file = input_file

            self.stamp_print('Successfully configured input {} file...'.format(file_type))
            return True

    def check_input_files(self):
        """Check input files"""

        input_vector = self.config_data_file(self.vector_file, 'vector')
        input_raster = self.config_data_file(self.raster_file)
        if input_vector and input_raster:
            self.stamp_print('Successfully configured input file paths...')
        else:
            self.stamp_print('An error occurred:')
            self.stamp_print('Found Input CSV: {}'.format(input_vector))
            self.stamp_print('Found Input Raster: {}'.format(input_raster))

            exit()

    def set_input_crs(self):
        """Set input CSV CRS"""

        p = Proj(init='epsg:{}'.format(self.epsg_code))
        self.input_crs = p

    def config_output_file(self):
        """Build output file path"""

        stamp = datetime.datetime.now()
        file_name = '{}_{}_{}.{}'.format(self.output_file, stamp.strftime('%A'),
                                         stamp.strftime('%d'), self.output_file_type)
        file_path = os.path.join(self.data_dir, file_name)
        if os.path.exists(file_path):
            self.stamp_print('Output file exists, preparing to overwrite...')
            try:
                os.remove(file_path)
            except OSError, e:
                raise e

        self.output_file = file_path
        self.stamp_print('Successfully configured output file...')

    def write_geojson(self):
        pass

    def write_csv(self):
        pass

    def write_shp(self):
        pass

    def get_coordinate_list(self):
        """Create coordinate list to be used for sampling"""

        df = GDF.from_file(self.vector_file)
        df.set_index('id', inplace=True)
        df['coords'] = df.apply(lambda row: Point([float(row['longitude']), float(row['latitude'])]), axis=1)
        df.set_geometry('coords', crs=self.input_crs, inplace=True, drop=True)
        df.sort_index(inplace=True)

        coords = []
        for i in df.iterfeatures():
            coords.append(i['geometry']['coordinates'])
        return coords

    def get_site_rad_level(self):
        """Perform sampling and write output"""

        fp = open(self.output_file, 'w')

        coords = self.get_coordinate_list()
        with rasterio.open(self.raster_file) as rst:
            result = rst.sample(coords)
            vals = list(result)
            for i in coords:
                ix = coords.index(i)
                val = vals[ix]
                fp.write('{}, {}, {}\n'.format(ix, i, val))

        fp.close()
        self.stamp_print('Scripts finished successfully. Output file: {}'.format(self.output_file))

