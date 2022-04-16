# Django imports
from django.urls import path
# Local imports
from registration.views import login_view, register, logout_view

app_name = 'registration'

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register, name="register"),
    path('logout/', logout_view, name="logout")
]
