import logging
import pyproj
import json
logger = logging.getLogger(__name__)

def lamber93_to_gps(x, y):
    """Function that transforms Lamber93 corrdinates to gps coordinates"""
    try:
        lambert = pyproj.Proj('+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
        wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        # x = 102980
        # y = 6847973
        long, lat = pyproj.transform(lambert, wgs84, x, y)
        return long, lat
    except Exception as e:
        logger.warning("There was an exception excecuting lamber93_to_gps")
        logger.exception(e)
        return None



def csv_to_dict(path):
    """Function thtat transforms a csv file to a python list of dictionaries"""
    try:   
        with open(path, 'r') as f:
            lines = f.readlines()
        headers = lines[0].strip().split(';')

        data = []
        for line in lines[1:]:
            values = line.strip().split(';')
            row = dict(zip(headers, values))
            data.append(row)
        # print(data[:10])
        return data
    except Exception as e:
        logger.warning("There was an exception excecuting csv_to_dict")
        logger.exception(e)
        return None


def create_shorter_coverage_gps(precision=1000000):
    """Function that creates a file with coverage data transformed from lamber93 to gps and truncates coordinates (x,y) to 6 digits (city level and API type response)"""
    coverage_list = csv_to_dict('coverage.csv')
    new_file = 'coverage_gps_short.csv'
    if coverage_list is not None:
        try:
            with open(new_file, "w") as file:
                headers = ";".join(coverage_list[0].keys())
                file.write(headers)
                file.write('\n')
                for coverage in coverage_list:
                    coord = lamber93_to_gps(coverage['x'], coverage['y'])
                    if coord:
                        file.write("{};{};{};{};{};{}".format(coverage['Operateur'], float(int(coord[0]*precision))/precision, float(int(coord[1]*precision))/precision,coverage['2G'], coverage['3G'], coverage['4G']))
                        file.write('\n')
            return new_file
        except Exception as e:
            logger.warning("There was an exception excecuting create_shorter_coverage_gps")
            logger.exception(e)
    
    return None

def save_json_file(path, dict):
    """Function that saves a json file"""
    try:
        with open(path, 'w') as f:
            json.dump(dict, f)
    except Exception as e:
        logger.warning("There was an exception excecuting save_json_file: {}".format(str(path)))
        logger.exception(e)
        return None
    


def creating_json_data_source_from_csv(path):
    """Function that creates json file from a csv file"""
    data_source_dict = {}
    duplicated_recods_equals = {}
    duplicated_recods_different = {}
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                # print(line)
                values_line = line.split(";")
                key = "{};{}".format(values_line[1], values_line[2])
                existing_record = data_source_dict.get(key, None)
                # Doesn'y exist record for key
                if existing_record is None:
                    data_source_dict[key] = {
                        values_line[0]: [
                            True if values_line[3] == "1" else False,
                            True if values_line[4] == "1" else False,
                            True if values_line[5] == "1" else False
                        ]
                    }
                # Exists coordenates but with not the same operateur
                elif values_line[0] not in existing_record.keys():
                    data_source_dict[key][values_line[0]] = [
                            True if values_line[3] == "1" else False,
                            True if values_line[4] == "1" else False,
                            True if values_line[5] == "1" else False
                    ]
                # Already exists record for coordinates and operateur. 
                else:
                    # Exists with same coverage values
                    if ((True if values_line[3] == '1' else False) == existing_record[values_line[0]][0]) and ((True if values_line[4] == '1' else False) == existing_record[values_line[0]][1]) and ((True if values_line[5] == '1' else False) == existing_record[values_line[0]][2]):
                        # add new key if not exists already
                        if not key in duplicated_recods_equals.keys():
                            duplicated_recods_equals[key] = {
                                values_line[0]: [
                                    True if values_line[3] == "1" else False,
                                    True if values_line[4] == "1" else False,
                                    True if values_line[5] == "1" else False
                                ]
                            }                            
                    # Already exists record for coordinates and operateur with different values
                    else:
                        # Add new duplicated different
                        if duplicated_recods_different.get(key, None) is None:
                            duplicated_recods_different[key] = {
                                    values_line[0]: [
                                        [
                                            True if values_line[3] == "1" else False,
                                            True if values_line[4] == "1" else False,
                                            True if values_line[5] == "1" else False
                                        ],
                                        [
                                            existing_record[values_line[0]][0],
                                            existing_record[values_line[0]][1],
                                            existing_record[values_line[0]][2],
                                        ]
                                    ]
                                }
                        # It already exists key 
                        else:
                            # Add new operateur to existing key in duplicated different
                            if not values_line[0] in duplicated_recods_different[key].keys():
                                duplicated_recods_different[key][values_line[0]] = [
                                    [
                                        True if values_line[3] == "1" else False,
                                        True if values_line[4] == "1" else False,
                                        True if values_line[5] == "1" else False
                                    ],
                                    [
                                        existing_record[values_line[0]][0],
                                        existing_record[values_line[0]][1],
                                        existing_record[values_line[0]][2],
                                    ]
                                ]
                            # Add new different coverage to existing operateur in existing key in duplicated different
                            else:
                                duplicated_recods_different[key][values_line[0]].append(
                                    [
                                        True if values_line[3] == "1" else False,
                                        True if values_line[4] == "1" else False,
                                        True if values_line[5] == "1" else False
                                    ],  
                                )
            
    except Exception as e:
        logger.warning("There was an exception excecuting creating_json_data_source while creating dictionaries")
        logger.exception(e)
        return None
    
    # Save all jsons files
    save_json_file("coverage.json", data_source_dict)
    save_json_file("duplicated_equals.json", duplicated_recods_equals)
    save_json_file("duplicated_different.json", duplicated_recods_different)

    return True


def transform_data_init(precision):
    """Function to be executed at the begining of the server to transform data on csv to json """

    # First creates file with coordinates transformed to gps and shortened
    new_file = create_shorter_coverage_gps(precision)
    if not new_file:
        return None
    
    # Second create json file 
    result = creating_json_data_source_from_csv(new_file)

    if result:
        logger.info("Executed correctly all migrations to json")
        return True
    
    logger.error("Executed migrations to json with errors")
    return False

transform_data_init(1000)
        




    
