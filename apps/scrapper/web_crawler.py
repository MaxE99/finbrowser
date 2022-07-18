# Python import
from django.shortcuts import get_object_or_404
import requests
from bs4 import BeautifulSoup
import html
from datetime import datetime
# Local import
from apps.article.models import Article
from apps.source.models import Source
from apps.logic.services import single_notification_create


def crawl_thegeneralist(articles):
    try:
        page = requests.get("https://www.readthegeneralist.com/briefings", headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'})
        soup = BeautifulSoup(page.content, 'lxml')
        for article in soup.find_all("div", class_="w-dyn-item"):
            link_tag = article.find("a", class_="single-article-wrap", href=True)
            info_container = article.find("div", class_="single-article-info-wrap v2")
            link = f"https://www.readthegeneralist.com{link_tag['href']}"
            pub_date = info_container.find("div", class_="published-date v2").text
            pub_date = datetime.strptime(pub_date.replace(",", ""), '%B %d %Y')
            title = info_container.find("div", class_="single-article-title v2").text
            title = html.unescape(title)
            source = get_object_or_404(Source, name="The Generalist")
            if articles.filter(title=title, link=link, pub_date=pub_date, source=source).exists():
                break
            else:
                created_article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source)
                single_notification_create(created_article)
    except:
        pass


def crawl_ben_evans(articles):
    try:
        page = requests.get("https://www.ben-evans.com/", headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'})
        soup = BeautifulSoup(page.content, 'lxml')
        for article in soup.find_all("div", class_="summary-content"):
            pub_date = article.find("time", class_="summary-metadata-item").text
            pub_date = datetime.strptime(pub_date.replace(",", ""), '%b %d %Y')
            title_with_link_tag = article.find("a", class_="summary-title-link")
            link = f"https://www.ben-evans.com{title_with_link_tag['href']}"
            title = title_with_link_tag.text
            title = html.unescape(title)
            source = get_object_or_404(Source, name="Benedict Evans")
            if articles.filter(title=title, link=link, pub_date=pub_date, source=source).exists():
                break
            else:
                created_article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source)
                single_notification_create(created_article)
    except:
        pass


def crawl_meritechcapital(articles):
    try:
        page = requests.get("https://www.meritechcapital.com/insights", headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'})
        soup = BeautifulSoup(page.content, 'lxml')
        for article in soup.find_all("a", class_="BlogLandingPage_card__FtA_n"):
            body_container = article.find("div", class_="BlogPostCard_body__knqKE")
            title = body_container.find("h3", class_="BlogPostCard_title__dnPww").text
            pub_date = body_container.find_all("span")[-1].text
            pub_date = datetime.strptime(pub_date.replace(",", "").replace(" | ", ""), '%b %d %Y')
            link = f"https://www.meritechcapital.com{article['href']}"
            title = html.unescape(title)
            source = get_object_or_404(Source, name="Meritech Capital")
            if articles.filter(title=title, link=link, pub_date=pub_date, source=source).exists():
                break
            else:
                created_article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source)
                single_notification_create(created_article)
    except:
        pass


def crawl_stockmarketnerd(articles):
    try:
        page = requests.get("https://stockmarketnerd.beehiiv.com/", headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'})
        soup = BeautifulSoup(page.content, 'lxml')
        for article in soup.find_all("div", class_="p-8"):
            link_tag = article.find("a", class_="hover:bg-gray-100")
            link = f"https://stockmarketnerd.beehiiv.com{link_tag['href']}"
            title = article.find("h2").text
            pub_date = article.find("time").text
            pub_date = datetime.strptime(pub_date.replace(",", ""), '%B %d %Y')
            title = html.unescape(title)
            source = get_object_or_404(Source, name="Stock Market Nerd")
            if articles.filter(title=title, link=link, pub_date=pub_date, source=source).exists():
                break
            else:
                created_article = Article.objects.create(title=title, link=link, pub_date=pub_date, source=source)
                single_notification_create(created_article)
    except:
        pass