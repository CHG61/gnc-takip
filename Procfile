web: bash -c "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn gncsite.wsgi:application --log-file -"
