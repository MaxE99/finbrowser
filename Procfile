release: python manage.py migrate
web: gunicorn researchbrowserproject.wsgi
main_worker: celery -A researchbrowserproject worker --beat --loglevel=info
