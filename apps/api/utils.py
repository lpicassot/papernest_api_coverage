import pyproj
import requests
import logging
import json

logger = logging.getLogger(__name__)


# ========= Main Functions =========

def get_address(q):
    """Function to retrieve detailed data from an address, using provided API """
    url = 'https://api-adresse.data.gouv.fr/search/?q={}'.format(q)
    try:
        response = requests.get(url)
        print(response.status_code)
        if response.status_code == 200:
            # print(response.text)
            return response.text
        return None
    except Exception as e:
        logger.warning("There was an exception excecuting get_address")
        logger.exception(e)
        return None


def get_coverage_data():
    """Function that retrieves JSON file"""
    try:
        path = 'coverage.json'
        with open(path, 'r') as json_file:
                results = json.load(json_file)
        return results
    except Exception as e:
        logger.warning("There was an exception excecuting get_coverage_data")
        logger.exception(e)
        return None
    
def get_coverage(coordinates):
    """Function that returns a coverage based on coordinates provided"""
    try:
        coverage_data = get_coverage_data()
        if coverage_data:
            # Get the precision of the coordinate
            element = next(iter(coverage_data.keys()))
            precision = len(element.split(';')[0].split('.')[1])
            # Get the coverage
            coordinate_x = str(coordinates[0]).split('.')[0] + "." + str(coordinates[0]).split('.')[1][:precision]
            coordinate_y = str(coordinates[1]).split('.')[0] + "." + str(coordinates[1]).split('.')[1][:precision]
            key = '{};{}'.format(coordinate_x, coordinate_y)

            coverage = coverage_data.get(key, None)

            # If coverage not found, look for the closest with 1 digit top of coordinate moovement
            if not coverage:            
                step = 0.001
                cicle = 0

                coordinate_x = float(coordinate_x)
                coordinate_y = float(coordinate_y)
                for i in range(10):
                    for j in range(1, 10):

                        while cicle < 8:

                            if cicle % 8 == 0:
                                new_coordinate_x = round(coordinate_x + step * i, 3)
                                new_coordinate_y = round(coordinate_y,3)
                            elif cicle % 8 == 1:
                                new_coordinate_x = round(coordinate_x - step * i, 3)
                                new_coordinate_y = round(coordinate_y,3)
                            elif cicle % 8 == 2:
                                new_coordinate_x = round(coordinate_x,3)
                                new_coordinate_y = round(coordinate_y + step * j,3)
                            elif cicle % 8 == 3:
                                new_coordinate_x = round(coordinate_x,3)
                                new_coordinate_y = round(coordinate_y - step * j,3)
                            elif cicle % 8 == 4:
                                new_coordinate_x = round(coordinate_x + step * i,3)
                                new_coordinate_y = round(coordinate_y + step * j,3)
                            elif cicle % 8 == 5:
                                new_coordinate_x = round(coordinate_x - step * i,3)
                                new_coordinate_y = round(coordinate_y - step * j,3)
                            elif cicle % 8 == 6:
                                new_coordinate_x = round(coordinate_x + step * i,3)
                                new_coordinate_y = round(coordinate_y - step * j,3)
                            elif cicle % 8 == 7:
                                new_coordinate_x = round(coordinate_x - step * i,3)
                                new_coordinate_y = round(coordinate_y + step * j,3)

                            cicle += 1
                            key = '{};{}'.format(new_coordinate_x, new_coordinate_y)

                            coverage = coverage_data.get(key, None)
                            if coverage:
                                return coverage
                        # Restart cicle 
                        cicle = 0
 
            return coverage
    except Exception as e:
        logger.warning("There was an exception excecuting get_coverage")
        logger.exception(e)
        return None


    
def get_provider_name(name):
    """Function to retrieves provider name from code"""
    CHOICES = {
        '20801':'Orange',
        '20810':'SFR',
        '20815':'Fee',
        '20820':'Bouygue'
    }

    return CHOICES.get(name, None)
    

        
        

# HACK:
# ========== Check Compatibility functions, Used to analyze data consistancy. ========== 
# ========== ---> They are Not Used for the functionality of the App <--- ========== 


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
    

def csv_to_list(path):
    """Function thtat transforms a csv file to a python list of strings"""
    try:
        final_list = []
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                final_list.append(line.replace('\n', ''))
        return final_list
    except Exception as e:
        logger.warning("There was an exception excecuting csv_to_list")
        logger.exception(e)
        return None

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

def create_coverage_gps():
    """Function that creates a file with coverage data transformed from lamber93 """
    coverage_list = csv_to_dict('coverage.csv')
    with open('coverage_gps_long.csv', "w") as file:
        headers = ";".join(coverage_list[0].keys())
        file.write(headers)
        file.write('\n')
        for coverage in coverage_list:
            coord = lamber93_to_gps(coverage['x'], coverage['y'])
            file.write("{};{};{};{};{};{}".format(coverage['Operateur'], coord[0], coord[1],coverage['2G'], coverage['3G'], coverage['4G']))
            file.write('\n')



def check_compatibility():
    """Function that checks if coverage data with truncated coordinates (6 digits) has multiple possible values"""
    path = 'coverage_gps_short.csv'
    check_data = csv_to_dict(path)
    # print(check_data[:10])
    results_not_ok = []
    results_not_ok_set = set()
    superpositions_ok = 0
    elements_retrieved = 0
    for idx, element in enumerate(check_data):
        elements_retrieved += 1
        for element2 in check_data[idx:]:
            if element['Operateur'] == element2['Operateur'] and element['x'] == element2['x'] and element['y'] == element2['y']:
                if element['2G'] == element2['2G'] and element['3G'] == element2['3G'] and element['4G'] == element2['4G']:
                    superpositions_ok += 1
                else:
                    results_not_ok.append(
                        {
                          'element1': {
                            'Operateur': element['Operateur'],
                            'x': element['x'],
                            'y': element['y'],
                            '2G': element['2G'],
                            '3G': element['3G'],
                            '4G': element['4G']
                          },
                          'element2': {
                            'Operateur': element2['Operateur'],
                            'x': element2['x'],
                            'y': element2['y'],
                            '2G': element2['2G'],
                            '3G': element2['3G'],
                            '4G': element2['4G']
                          },
                        })
                    results_not_ok_set.add("{};{};{}".format(element['Operateur'], element['x'], element['y']))
    with open('results_not_ok.csv', "w") as file:
        headers = "Operateur;x;y;2G-1;3G-1;4G-1;2G-2;3G-2;4G-2"
        file.write(headers)
        file.write('\n')
        for result in results_not_ok:
            file.write("{};{};{};{};{};{};{};{};{}".format(result['element1']['Operateur'],result['element1']['x'],result['element1']['y'],result['element1']['2G'],result['element1']['3G'],result['element1']['4G'],result['element2']['2G'],result['element2']['3G'],result['element2']['4G']))
            file.write('\n')

    with open('results_not_ok_list.csv', "w") as file:
        for result in set(results_not_ok):
            file.write("{};{};{}".format(result['element1']['Operateur'],result['element1']['x'],result['element1']['y']))
            file.write('\n')

    with open('results_not_ok_set.csv', "w") as file:
        for result in set(results_not_ok_set):
            file.write(result)
            file.write('\n')

    return elements_retrieved, superpositions_ok, results_not_ok


def check_consistancy_gps_long_data():
    path1 = 'coverage_gps_long.csv'
    coverage_long = csv_to_dict(path1)
    path2 = 'results_not_ok_set.csv'
    results_not_ok = csv_to_list(path2)


    coverage_long_no_ok = []
    coverage_sets_no_ok = set()
    coverage_short_no_ok = []

    for idx, coverage in enumerate(coverage_long):
        try:
            # First: check for every value of the sets of not ok, if the coverage has correct values. If not, create file with all values (operateur - x - y) that are not to be trusted
            coverage_operateur = coverage['Operateur']
            coverage_x = str(float(int(float(coverage['x']) * 1000000)) / 1000000)
            coverage_y = str(float(int(float(coverage['y']) * 1000000)) / 1000000)
            to_check = "{};{};{}".format(coverage_operateur, coverage_x, coverage_y)

            if to_check in results_not_ok:
                for coverage2 in coverage_long[idx:]:
                    if coverage['Operateur'] == coverage2['Operateur'] and coverage['x'] == coverage2['x'] and coverage['y'] == coverage2['y']:
                        if coverage['2G'] != coverage2['2G'] or coverage['3G'] != coverage2['3G'] or coverage['4G'] != coverage2['4G']:
                            coverage_long_no_ok.append(coverage)
                            coverage_sets_no_ok.add("{};{};{}".format(coverage['Operateur'], coverage['x'], coverage['y']))
                        elif "{};{};{}".format(coverage['Operateur'], coverage['x'], coverage['y']) not in coverage_sets_no_ok:
                                coverage_short_no_ok.append(coverage)
 
        except Exception as e:
            print("Exception with: ----------------")
            print(e)


    with open('checked_long_not_ok.csv', "w") as file:
        for result in coverage_long_no_ok:
            file.write("{};{};{};{};{};{}".format(result['Operateur'], result['x'], result['y'], result['2G'], result['3G'], result['4G']))
            file.write('\n')
    with open('checked_short_not_ok.csv', "w") as file:
        for result in coverage_short_no_ok:
            file.write("{};{};{};{};{};{}".format(result['Operateur'], result['x'], result['y'], result['2G'], result['3G'], result['4G']))
            file.write('\n')
    return    




    