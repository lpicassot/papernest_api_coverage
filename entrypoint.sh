#!/bin/sh
echo "Startinggg"

# Migrate Database
python manage.py migrate
# Execute python script to create json files
# python init.py

# Start server. 
echo "Start Webserver"
python manage.py runserver 0.0.0.0:8000

