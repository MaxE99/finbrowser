# Django imports
from django.urls import path
# Local imports
from registration.views import login_view, register

app_name = 'registration'

urlpatterns = [
    path('login/', login_view, name="registration-login"),
    path('register/', register, name="registration-register")
]
