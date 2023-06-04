# Python imports
import html
from datetime import datetime
from django.db.models import Q

# Local imports
from apps.source.models import Source, SourceTag, Website
from apps.sector.models import Sector


def filter_sources(get_request):
    websites = get_request.getlist("website")
    sectors = get_request.getlist("sector")
    tags = get_request.getlist("tag")
    content = get_request.getlist("content")
    paywall = get_request.getlist("paywall")
    top_sources = get_request.getlist("top_sources_only")
    q_objects = Q()
    if websites:
        websites = Website.objects.filter(name__in=websites)
        q_objects.add(Q(website__in=websites), Q.AND)
    if sectors:
        sectors = Sector.objects.filter(name__in=sectors)
        q_objects.add(Q(sector__in=sectors), Q.AND)
    if tags:
        tags = SourceTag.objects.filter(name__in=tags)
        q_objects.add(Q(tags__in=tags), Q.AND)
    if content and len(content) < 3:
        q_objects.add(Q(content_type__in=content), Q.AND)
    if paywall:
        q_objects.add(Q(paywall__in=paywall), Q.AND)
    if top_sources:
        q_objects.add(Q(top_source=True), Q.AND)
    return (
        Source.objects.select_related("website", "sector")
        .prefetch_related("tags")
        .filter(q_objects)
        .order_by("-average_rating", "-ammount_of_ratings")
        .distinct()
    )


def article_components_get(item, description=False):
    """Goes through xml item and returns title, link and publishing date of article."""

    # some titles in the xml files have been escaped twice which makes it necesseary to ecape the titles more than once
    def double_escaped_string_unescape(title):
        unescaped = ""
        while unescaped != title:
            title = html.unescape(title)
            unescaped = html.unescape(title)
        return title

    link = item.find(".//link").text
    pub_date = item.find(".//pubDate").text[:-4]
    pub_date = datetime.strptime(
        pub_date.replace(" -", "").replace(" +", ""), "%a, %d %b %Y %X"
    )
    title = double_escaped_string_unescape(item.find(".//title").text)
    if description:
        description = double_escaped_string_unescape(item.find(".//description").text)
        title_with_desc = f"{title}: {description}"[0:500]
        return title_with_desc, title, link, pub_date
    return None, title, link, pub_date
