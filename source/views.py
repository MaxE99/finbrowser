# Django import
from django.shortcuts import render
# Local import
from home.models import Source


def profile(request, source):
    source = Source.objects.get()
    return render(request, 'source/profile.html')
