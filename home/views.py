# Django imports
from django.shortcuts import redirect, render
from django.core.cache import cache
from django.contrib import messages
# Local imports
from home.models import BrowserSource, BrowserCategory, List, Sector
from home.forms import AddSourceForm


def browser(request):
    if "selectSearchSettings" in request.POST:
        sources = request.POST.getlist('sources')
        timeframe = request.POST.get('timeframe')
        search_term = request.POST.get('search_term')
        cache.set_many({
            'sources': sources,
            'timeframe': timeframe,
            'search_term': search_term
        })
    elif "addSourcesSettings" in request.POST:
        print("ACTIVATED")
        add_source_form = AddSourceForm(request.POST)
        if add_source_form.is_valid():
            print("IS VALID")
            add_source_form.save()
            messages.success(request, f'Source has been added!')
            return redirect('../../home/browser/')
    add_source_form = AddSourceForm()
    browser_sources = BrowserSource.objects.all().order_by('source')
    browser_categories = BrowserCategory.objects.all().order_by('name')
    return render(
        request, 'home/browser.html', {
            'browser_categories': browser_categories,
            'browser_sources': browser_sources,
            'add_source_form': add_source_form,
        })


def lists(request):
    lists = List.objects.all()
    return render(request, 'home/lists.html', {'lists': lists})


def sectors(request):
    sectors = Sector.objects.all()
    return render(request, 'home/sectors.html', {'sectors': sectors})