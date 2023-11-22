web: sh -c 'cd backend_api && python manage.py collectstatic --noinput && python manage.py migrate && gunicorn backend_api.wsgi:application'
