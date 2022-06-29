release: python manage.py migrate
web: gunicorn researchbrowserproject.wsgi
worker: celery -A apps.scrapper.tasks worker -B --loglevel=info
