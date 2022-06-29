release: python manage.py migrate
web: gunicorn researchbrowserproject.wsgi
main_worker: python manage.py celery worker --beat --loglevel=info
