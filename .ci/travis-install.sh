#!/usr/bin/env bash

set -e -x

pip install -r requirements.txt
python manage.py migrate