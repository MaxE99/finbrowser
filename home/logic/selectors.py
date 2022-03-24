# Django imports
from django.conf import settings
from django.core.cache import cache
# Python imports
import html
from urllib.request import Request, urlopen
import concurrent.futures
import os
import xml.etree.cElementTree as ET
import requests
from datetime import datetime, timedelta
import concurrent.futures
# Local imports
from home.models import BrowserSource
from home.logic.pure_logic import timeframe_check


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


def file_creation_date_check(domain, sources):
    """Checks file creation date of xml files to see when sources were last scraped.
    If the last time was over 12 hours ago sources are scrapped again. The reason
    for this is to not allow to many requests to substacks (danger of IP-Ban)"""
    modification_date = datetime.fromtimestamp(
        os.path.getmtime(
            os.path.join(settings.XML_FILE_DIRECTORY, f'{domain}.xml')))
    if (datetime.now() - modification_date) > timedelta(hours=12):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(xml_scrape, sources)


def source_data_get(domain):
    """Goes through the scraped xml file and returns root (article data) and favicon"""
    data = ET.parse(os.path.join(settings.XML_FILE_DIRECTORY, f'{domain}.xml'))
    root = data.getroot()
    if os.path.isfile(
            os.path.join(settings.FAVICON_FILE_DIRECTORY,
                         f'{domain}.png')) == False:
        source_picture = root.find('.//url').text
        img_data = requests.get(source_picture).content
        with open(
                os.path.join(settings.FAVICON_FILE_DIRECTORY, f'{domain}.png'),
                'wb') as handler:
            handler.write(img_data)
    favicon = f'home/favicons/{domain}.png'
    return root, favicon


def website_scrapping_initiate(source, domain):
    """Inititates web scrapping process. Returns True if sucessfull and False
    when a problem occured during the process."""
    try:
        if not BrowserSource.objects.filter(domain=domain).exists():
            xml_scrape(source, domain)
            _, _ = source_data_get(domain)
        return True
    except Exception:
        return False


def xml_scrape(source, domain):
    """Scrapes the xml feed of given source and writes it to a xml file on 
    local directory."""
    feed_url = f'{source}feed'
    req = Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
    website_data = urlopen(req)
    website_xml = website_data.read()
    website_data.close()
    with open(os.path.join(settings.XML_FILE_DIRECTORY, f'{domain}.xml'),
              'wb') as f:
        f.write(website_xml)
