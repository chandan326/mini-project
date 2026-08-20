#!/bin/bash
echo "Installing dependencies..."
python3.11 -m pip install -r requirements.txt

echo "Collecting static files..."
python3.11 manage.py collectstatic --noinput --clear
