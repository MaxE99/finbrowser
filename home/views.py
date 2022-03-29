# Django imports
from django.shortcuts import redirect, render
from django.core.cache import cache
from django.contrib import messages
from datetime import timedelta, date
# Local imports
from home.models import BrowserSource, BrowserCategory, List, Sector
from home.forms import AddSourceForm, AddListForm


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
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST)
        if add_list_form.is_valid():
            add_list_form.save()
            messages.success(request, f'List has been created!')
            return redirect('../../home/lists/')
    timeframe = cache.get('timeframe')
    content_type = cache.get('content_type')
    sources = cache.get('sources')
    if timeframe and timeframe != 'All':
        lists = List.objects.filter(updated_at__gte=date.today() -
                                    timedelta(days=int(timeframe)))
    if content_type and content_type != 'All':
        lists = lists.filter(content_type=content_type)
    if sources and sources != 'All':
        lists = lists.filter(main_website_source=sources)
    else:
        lists = List.objects.all()
    cache.delete_many(['timeframe', 'content_type', 'sources'])
    add_list_form = AddListForm()
    return render(request, 'home/lists.html', {
        'add_list_form': add_list_form,
        'lists': lists,
    })


def sectors(request):
    sectors = Sector.objects.all()
    return render(request, 'home/sectors.html', {'sectors': sectors})