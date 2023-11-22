web: sh -c 'cd backend_api && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn backend_api.wsgi:application'
