# Django imports
from django.core.cache import cache
# Python imports
import html
from datetime import datetime
# Local imports
from home.models import BrowserSource
from home.logic.pure_logic import timeframe_check
from home.logic.scrapper import source_data_get, file_creation_date_check


def article_components_get(item):
    """Goes through xml item and returns title, link and publishing date of article."""

    # some titles in the xml files have been escaped twice which makes it necesseary to ecape the titles more than once
    def double_escaped_string_unescape(title):
        unescaped = ""
        while unescaped != title:
            title = html.unescape(title)
            unescaped = html.unescape(title)
        return title

    title = double_escaped_string_unescape(item.find('.//title').text)
    link = item.find('.//link').text
    pub_date = item.find('.//pubDate').text[:-4]
    pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %X')
    return title, link, pub_date


def articles_search():
    """Search for articles when search site is opened or search settings are saved. If avaiable the search 
    parameters: sources, timeframe and search_term are used, otherwise it performs a standard search without
    parameters."""
    articles = []
    sources = cache.get('sources')
    timeframe = cache.get('timeframe')
    search_term = cache.get('search_term')
    selected_sources = []
    targeted_search = True
    if sources is None:
        targeted_search = False
        sources = BrowserSource.objects.all()
        for source in sources:
            selected_sources.append(source)
    else:
        for domain in sources:
            try:
                source = BrowserSource.objects.filter(domain=domain)
                selected_sources.append(source)
            except:
                continue

    for source in selected_sources:
        if targeted_search:
            file_creation_date_check(
                selected_sources[int(len(selected_sources) / 2)][0],
                selected_sources)
            root, favicon = source_data_get(source[0])
        else:
            file_creation_date_check(
                selected_sources[int(len(selected_sources) / 2)],
                selected_sources)
            root, favicon = source_data_get(source)
        for item in root.findall('.//item'):
            try:
                title, link, pub_date = article_components_get(item)
                time_since_pub = datetime.utcnow() - pub_date
                if search_term != None or str(search_term) != 'None':
                    if search_term in title:
                        if timeframe != None or str(timeframe) != "None":
                            timeframe_check(timeframe, time_since_pub,
                                            articles, favicon, title, link,
                                            pub_date)
                else:
                    timeframe_check(timeframe, time_since_pub, articles,
                                    favicon, title, link, pub_date)
            except:
                continue
    return articles
