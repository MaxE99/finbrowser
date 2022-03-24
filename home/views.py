# Django imports
from django.shortcuts import redirect, render
from django.core.cache import cache
from django.contrib import messages
# Local imports
from home.logic.selectors import articles_search, website_scrapping_initiate
from home.logic.pure_logic import paginator_create
from home.models import BrowserSource, BrowserCategory, List
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
    # search_settings_form = SearchSettingsForm()
    add_source_form = AddSourceForm()
    browser_sources = BrowserSource.objects.all().order_by('source')
    browser_categories = BrowserCategory.objects.all().order_by('name')
    # search_articles = articles_search()
    # search_articles, page = paginator_create(request, search_articles, 18)
    return render(
        request,
        'home/browser.html',
        {
            # 'search_articles': search_articles,
            # 'page': page,
            'browser_categories': browser_categories,
            'browser_sources': browser_sources,
            # 'search_settings_form': search_settings_form,
            'add_source_form': add_source_form,
        })


def lists(request):
    lists = List.objects.all()
    return render(request, 'home/lists.html', {'lists': lists})