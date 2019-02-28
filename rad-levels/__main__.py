import argparse
from radiation_levels import RadiationLevels


def get_args():
    parser = argparse.ArgumentParser(description='Get Radiation Levels At Specific Coordinates')
    parser.add_argument('vector', help='Vector file with point features representing sites')
    parser.add_argument('raster', help='Irradiation raster data set')
    parser.add_argument('--data_dir', help='Name of the directory containing working files', default='data')
    parser.add_argument('--epsg', type=int, help='EPSG code for the CRS of the input CSV', default=4326)
    parser.add_argument('--out_file_prefix', help='Prefix for the output file', default='Output')
    parser.add_argument('--out_file_type', help='Output vector file type', default='csv')
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    args_dict = get_args()

    Tool = RadiationLevels(**args_dict)
    Tool.print_initial()
    Tool.config_data_dir()
    Tool.check_input_files()
    Tool.config_output_file()
    Tool.set_input_crs()
    Tool.get_site_rad_level()
