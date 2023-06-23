# Papernest API

### Installation and Execution

1. Clone this repository:

   ```
   git clone https://github.com/lpicassot/papernest_api_coverage.git
   cd papernest_api_coverage
   ```

2. Execute dockerfile

   ```
    docker build -t papernest_api .
    docker run --name papernest_api -p 8000:8000 papernest_api
   ```

3. Tests
   ```
   python3 manage.py test apps/api
   ```

### Considerations and Assumptions

1. The task required city-level precision.

2. In the search for the address, in case there is more than one possible solution, I have adopted the following policy:

   - The valid option will be the one with the highest "score" from the API.
   - The valid option must have a minimum score value set at 0.4.

3. In the event that the coordinates are not found in the database, as city-level precision is required,
   it looks for the coordinate that matches the one requested at the endpoint in the database, up to a maximum of 1 digit in the coordinates
   (there are larger and smaller cities, so approximating more than one digit could lead to providing erroneous data in the case of a small city).

4. The algorithm that searches for the nearest coordinate is not 100% correct since it first iterates with all the "y" values and then moves on to the "x" values.
   It is also not optimized in terms of speed. Given the scope of this exercise, a possible solution is proposed, aware that it can be optimized in terms of precision and speed.

5. When modifying the database with the coverages, the digits are truncated, leaving only 3 as it is sufficient for city-level precision, as detailed in the task.
   In this truncation, duplications were later found for the same coordinate and operator, with different coverages.
   Analyzing the master file coverage.csv, the duplications were already present in the original database, having different data for the same coordinate and operator.

6. Given the above, in cases where a coordinate is requested that has more than one possible coverage data for a particular Operateur, and considering that the original database already presented inconsistencies,
   I made the decision to take the first coverage found. I have generated a file with the duplications that present more than one possible value: duplicated_different.json
   In production, I would make a request to the data provider to verify this information.

7. Given the scope of this exercise, I limit myself to using a .json file as a database, handling the data in memory.
   Ideally in production, I would use a non-relational database (like Mongo) for data storage.

8. An init.py file was created to transform the source data file coverage.csv into a json that will later be used to retrieve coverage from coordinates.
   This file is intended to be executed when runing container, before running server.
   The execution of this file is included in the entrypoint.sh, but it is commented as it may take up to a coouple of minutes to be fully executed.
   The output of the init.py is already included in the source code.
