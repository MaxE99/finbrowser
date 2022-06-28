from __future__ import absolute_import, unicode_literals
# Django Imports
from django.conf import settings
from celery import Celery
# Local Imports
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'researchbrowserproject.settings')
app = Celery('researchbrowserproject')
app.config_from_object(settings , namespace='CELERY')
app.autodiscover_tasks()