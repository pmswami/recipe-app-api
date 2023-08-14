#!/bin/sh

set -e

python manage.py wait_for_db # wait till db gets ready for new connections
python manage.py collectstatic --noinput #collect all static files
python manage.py migrate #migrate all changes to db
uwsgi --socket :9000 --workers 10 --master --enable-threads --module app.wsgi