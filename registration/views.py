# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
# Local imports
from accounts.models import PrivacySettings, Profile
from accounts.forms import UserCreationForm
from registration.forms import UserLoginForm


def register(request):
    if request.method == 'POST':
        user_creation_form = UserCreationForm(request.POST)
        if user_creation_form.is_valid():
            user = user_creation_form.save()
            profile = Profile.objects.create(user=user)
            PrivacySettings.objects.create(profile=profile)
            login(request, user)
            return redirect('home:feed')
    else:
        user_creation_form = UserCreationForm()
    context = {'user_creation_form': user_creation_form}
    return render(request, 'registration/register.html', context)


def login_view(request):
    if request.method == "POST":
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            cleaned_username = user_login_form.cleaned_data["username"]
            cleaned_password = user_login_form.cleaned_data["password"]
            user = authenticate(username=cleaned_username,
                                password=cleaned_password)
            if user:
                login(request, user)
                return redirect('home:feed')
            else:
                messages.error(
                    request,
                    "Error: Please enter a correct email and password!")
        else:
            messages.error(
                request, "Error: Please enter a correct email and password!")
    else:
        user_login_form = UserLoginForm()
    context = {'user_login_form': user_login_form}
    return render(request, 'registration/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('registration:login')