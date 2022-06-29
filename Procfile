release: python manage.py migrate
web: gunicorn researchbrowserproject.wsgi
main_worker: celery -A researchbrowserproject.celery worker --beat --loglevel=info
