web: sh -c 'cd backend_api && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn gen_zone.wsgi:application'
