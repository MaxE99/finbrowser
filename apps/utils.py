from django.core.paginator import Paginator, EmptyPage, Page, PageNotAnInteger


def create_paginator(
    request, queryset, objects_per_site: int, page_name: str = "page"
) -> Page:
    """
    Creates a paginator for the given queryset and retrieves the requested page of results.

    Args:
        request (Any): The HTTP request object containing pagination parameters.
        queryset (Any): The queryset to paginate.
        objects_per_site (int): The number of objects to display per page.
        page_name (str, optional): The query parameter name for the page number. Defaults to "page".

    Returns:
        Page: The objects for the requested page, or the first/last page if the requested page is invalid.
    """
    paginator = Paginator(queryset, objects_per_site)
    page = request.GET.get(page_name)

    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    return objects
