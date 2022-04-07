# Django imports
from django.urls import path
# Local imports
from registration.views import login_view, register, logout_view

app_name = 'registration'

urlpatterns = [
    path('login/', login_view, name="registration-login"),
    path('register/', register, name="registration-register"),
    path('logout/', logout_view, name="registration-logout")
]
