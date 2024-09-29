from typing import List

from django.db.models import Q

from apps.source.models import Source, SourceTag, Website
from apps.sector.models import Sector


def filter_sources(get_request) -> List[Source]:
    """
    Filter sources based on the provided GET request parameters.

    Args:
        get_request: The HTTP GET request containing filtering parameters.

    Returns:
        List[Source]: A list of filtered Source objects.
    """
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
