# Django imports
from django.conf import settings
# Python imports
from urllib.request import Request, urlopen
import concurrent.futures
import os
import xml.etree.cElementTree as ET
import requests
from datetime import datetime, timedelta
import concurrent.futures
# Local imports


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
