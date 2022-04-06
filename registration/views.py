from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from accounts.forms import RegisterForm


def login_view(request):
    if request.method == "POST":
        print("POST METHOD")
        user_login_form = AuthenticationForm(request.POST)
        if user_login_form.is_valid():
            print("IS VALID")
            user = user_login_form.get_user()
            login(request, user)
            return redirect('../../home/browser/')
    else:
        print("GET METHOD")
        user_login_form = AuthenticationForm()
    context = {'user_login_form': user_login_form}
    return render(request, 'registration/login.html', context)


def register(request):
    if request.method == 'POST':
        user_creation_form = RegisterForm(request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            return redirect('../../home/browser/')
    else:
        user_creation_form = RegisterForm()
    context = {'user_creation_form': user_creation_form}
    return render(request, 'registration/register.html', context)