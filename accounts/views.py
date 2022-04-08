# Django imports
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
# Local imports
from accounts.models import Profile


def profile(request, slug):
    profile = get_object_or_404(Profile, slug=slug)
    context = {'profile': profile}
    return render(request, 'accounts/profile.html', context)