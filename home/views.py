# Django imports
from django.shortcuts import redirect, render, get_object_or_404
from django.core.cache import cache
from django.contrib import messages
# Python imports
from operator import attrgetter
from datetime import timedelta, date
# Local imports
from home.models import Article, BrowserSource, BrowserCategory, List, Sector, Source
from home.forms import AddSourceForm, AddListForm
from home.logic.pure_logic import paginator_create


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
    filter_args = {
        'content_type': content_type,
        'main_website_source': sources
    }
    if timeframe != 'All' and timeframe != None:
        filter_args['updated_at__gte'] = date.today() - timedelta(
            days=int(timeframe))
    filter_args = dict(
        (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
    lists = List.objects.filter(**filter_args)
    # cache.delete_many(['timeframe', 'content_type', 'sources'])
    add_list_form = AddListForm()
    results_found = len(lists)
    lists = sorted(lists, key=attrgetter('likes'), reverse=True)
    lists, page = paginator_create(request, lists, 10)
    return render(
        request, 'home/lists.html', {
            'add_list_form': add_list_form,
            'lists': lists,
            'page': page,
            'results_found': results_found,
        })


def sectors(request):
    sectors = Sector.objects.all()
    return render(request, 'home/sectors.html', {'sectors': sectors})


def articles(request):
    timeframe = cache.get('articles_timeframe')
    sector = cache.get('articles_sector')
    paywall = cache.get('articles_paywall')
    sources = cache.get('articles_sources')
    filter_args = {'source__paywall': paywall, 'source__website': sources}
    if timeframe != 'All' and timeframe != None:
        filter_args['pub_date__gte'] = date.today() - timedelta(
            days=int(timeframe))
    filter_args = dict(
        (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
    search_articles = Article.objects.filter(
        **filter_args).order_by('-pub_date')
    # if sector != 'All' and timeframe != None:
    #     search_articles.filter(source__sectors=sector)
    results_found = len(search_articles)
    search_articles, page = paginator_create(request, search_articles, 10)
    sectors = Sector.objects.all().order_by('name')
    context = {
        'results_found': results_found,
        'search_articles': search_articles,
        'sectors': sectors
    }
    return render(request, 'home/articles.html', context)


def list_details(request, list_id):
    list = get_object_or_404(List, list_id=list_id)
    context = {'list': list}
    return render(request, 'home/list_details.html', context)


def sector_details(request, name):
    sector = get_object_or_404(Sector, name=name.capitalize())
    context = {'sector': sector}
    return render(request, 'home/sector_details.html', context)


def settings(request):
    return render(request, 'home/settings.html')


def main(request):
    return render(request, 'home/main.html')


def search_results(request, search_term):
    filtered_lists = List.objects.filter(name__istartswith=search_term)
    filtered_sources = Source.objects.filter(domain__istartswith=search_term)
    filtered_articles = Article.objects.filter(title__icontains=search_term)
    context = {
        'filtered_articles': filtered_articles,
        'filtered_lists': filtered_lists,
        'filtered_sources': filtered_sources,
        'search_term': search_term
    }
    return render(request, 'home/search_results.html', context)