# Django imports
from django.views.generic import TemplateView
# Local imports
from apps.mixins import BaseMixin


class MainView(TemplateView, BaseMixin):
    template_name = 'main/main.html'
