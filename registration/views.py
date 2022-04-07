from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from accounts.forms import UserCreationForm


def register(request):
    if request.method == 'POST':
        user_creation_form = UserCreationForm(request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            return redirect('../../home/browser/')
    else:
        user_creation_form = UserCreationForm()
    context = {'user_creation_form': user_creation_form}
    return render(request, 'registration/register.html', context)


def login_view(request):
    if request.method == "POST":
        user_login_form = AuthenticationForm(data=request.POST)
        if user_login_form.is_valid():
            cleaned_username = user_login_form.cleaned_data["username"]
            cleaned_password = user_login_form.cleaned_data["password"]
            user = authenticate(username=cleaned_username,
                                password=cleaned_password)
            if user:
                login(request, user)
                return redirect('../../home/browser/')
            else:
                pass  # user failed auth, send message back to user
        else:
            pass  # form not valid, handle errors
    else:
        user_login_form = AuthenticationForm()
    context = {'user_login_form': user_login_form}
    return render(request, 'registration/login.html', context)


def logout_view(request):
    # if request.method == "POST":
    logout(request)
    return redirect('../../registration/login/')