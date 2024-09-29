from django.db import models


class ListManager(models.Manager):
    """
    Custom manager for managing List instances.

    This manager provides methods to filter lists by their creator
    and to retrieve highlighted content associated with specific lists.
    """

    def filter_by_creator(self, user):
        """
        Filters the lists by the creator.

        Args:
            user: The user whose lists are to be retrieved.

        Returns:
            QuerySet: A queryset of lists created by the specified user,
            with related creator profiles and prefetched articles and sources.
        """
        return (
            self.filter(creator=user)
            .select_related("creator__profile")
            .prefetch_related("articles", "sources")
        )

    def get_highlighted_content(self, selected_list):
        """
        Retrieves highlighted content for a selected list.

        Args:
            selected_list: The list object or identifier for which
            highlighted content is to be retrieved.

        Returns:
            List[models.Model]: A list of articles related to the
            specified list, with selected related fields for efficient
            querying.
        """
        return (
            self.get(list_id=selected_list.list_id)
            .articles.all()
            .select_related("source", "source__website", "source__sector", "tweet_type")
        )
