from typing import Dict, Optional, Union

from django.db import models
from django.db.models import Sum


class SourceManager(models.Manager):
    """
    Custom manager for the Source model, providing methods for various source-related
    queries, including calculating similar sources, filtering by content type, sector,
    and subscription, as well as retrieving random top sources.
    """

    def calc_similiar_sources(self):
        """
        Calculates and sets the top 10 most similar sources for each source in the database.

        The similarity score is based on various attributes such as sector, content type,
        top source status, website, paywall, average rating, number of ratings, and shared tags.
        """
        sources = list(self.all().prefetch_related("tags"))

        for source in sources:
            sim_dict = {}

            for sim_source in sources:
                if source == sim_source:
                    continue

                score = 0

                if sim_source.sector == source.sector:
                    score += 5
                if sim_source.content_type == source.content_type:
                    score += 3
                if source.top_source and sim_source.top_source == source.top_source:
                    score += 3
                if sim_source.website == source.website:
                    score += 2
                if sim_source.paywall == source.paywall:
                    score += 2
                if source.ammount_of_ratings > 5:
                    if abs(source.average_rating - sim_source.average_rating) < 0.5:
                        score += 1
                    if (
                        abs(source.ammount_of_ratings - sim_source.ammount_of_ratings)
                        < source.ammount_of_ratings / 10
                    ):
                        score += 1

                for tag in sim_source.tags.all():
                    if tag in source.tags.all():
                        score += 3

                sim_dict[sim_source.source_id] = score

            similiar_sources = {
                k: v
                for k, v in sorted(
                    sim_dict.items(), key=lambda item: item[1], reverse=True
                )[0:10]
            }
            calc_sources = calc_sources = [k for k in similiar_sources]
            self.filter(pk=source.source_id).first().sim_sources.set(calc_sources)

    def filter_subscribed_sources_by_content_type(
        self, user
    ) -> Dict[str, models.QuerySet]:
        """
        Filters subscribed sources by content type for a specific user.

        Args:
            user: The user whose subscribed sources are to be retrieved.

        Returns:
            Dict[str, QuerySet]: A dictionary containing QuerySets of analysis, commentary,
            and news sources subscribed by the user.
        """
        subscribed_sources = self.filter_by_subscription(user)

        return {
            "analysis": subscribed_sources.filter(content_type="Analysis"),
            "commentary": subscribed_sources.filter(content_type="Commentary"),
            "news": subscribed_sources.filter(content_type="News"),
        }

    def filter_by_sector(self, sector: str) -> Dict[str, models.QuerySet]:
        """
        Filters sources by sector and content type.

        Args:
            sector (str): The sector to filter sources by.

        Returns:
            Dict[str, QuerySet]: A dictionary containing QuerySets of analysis, commentary,
            and news sources within the specified sector.
        """
        return {
            "analysis_sources": self.filter(content_type="Analysis", sector=sector),
            "commentary_sources": self.filter(content_type="Commentary", sector=sector),
            "news_sources": self.filter(content_type="News", sector=sector),
        }

    def filter_by_subscription(self, user) -> models.QuerySet:
        """
        Filters sources that are subscribed to by a specific user.

        Args:
            user: The user whose subscribed sources are to be retrieved.

        Returns:
            QuerySet: A QuerySet of subscribed sources containing specific fields for optimization.
        """
        return self.filter(subscribers=user).only(
            "favicon_path", "slug", "name", "average_rating", "source_id"
        )

    def filter_by_search_term(self, search_term: str) -> models.QuerySet:
        """
        Filters sources by a search term that matches the beginning of the source name.

        Args:
            search_term (str): The search term to filter sources by.

        Returns:
            QuerySet: A QuerySet of sources whose names start with the search term.
        """
        return self.filter(name__istartswith=search_term)

    def filter_by_list_and_search_term_exclusive(
        self, search_term: str, selected_list
    ) -> models.QuerySet:
        """
        Filters sources by a search term, excluding sources already in a selected list.

        Args:
            search_term (str): The search term to filter sources by.
            selected_list: The list whose sources should be excluded from the results.

        Returns:
            QuerySet: A QuerySet of sources filtered by the search term and excluding sources in the selected list.
        """
        return self.filter(name__istartswith=search_term).exclude(
            source_id__in=selected_list.sources.all()
        )

    def filter_by_subscription_and_search_term_exclusive(
        self, search_term: str, user
    ) -> models.QuerySet:
        """
        Filters sources by a search term, excluding sources subscribed to by a specific user.

        Args:
            search_term (str): The search term to filter sources by.
            user: The user whose subscribed sources should be excluded from the results.

        Returns:
            QuerySet: A QuerySet of sources filtered by the search term and excluding those the user is subscribed to.
        """
        return self.filter(name__istartswith=search_term).exclude(subscribers=user)

    def get_random_top_sources(self) -> models.QuerySet:
        """
        Retrieves a random selection of top sources.

        Returns:
            QuerySet: A QuerySet of 21 randomly ordered top sources.
        """
        return self.filter(top_source=True).order_by("?")[0:21]


class SourceRatingManager(models.Manager):
    """
    Manager class for handling operations related to the SourceRating model, including
    retrieving user ratings, calculating average ratings, counting total ratings, and saving user ratings.
    """

    def get_user_rating(self, user, source) -> Union[int, bool]:
        """
        Retrieves the rating given by a specific user for a specific source.

        Args:
            user (User): The user whose rating is being fetched.
            source (Source): The source for which the rating is being fetched.

        Returns:
            Union[int, bool]: The rating if it exists, otherwise False.
        """
        return (
            self.get(user=user, source=source).rating
            if self.filter(user=user, source=source).exists()
            else False
        )

    def get_average_rating(self, source) -> Optional[float]:
        """
        Calculates the average rating for a given source.

        Args:
            source (Source): The source for which the average rating is being calculated.

        Returns:
            Optional[float]: The average rating rounded to one decimal place, or None if there are no ratings.
        """
        list_ratings = self.filter(source=source)
        sum_ratings = self.filter(source=source).aggregate(Sum("rating"))
        sum_ratings = sum_ratings.get("rating__sum", None)
        return round(sum_ratings / list_ratings.count(), 1) if sum_ratings else None

    def get_amount_of_ratings(self, source) -> int:
        """
        Returns the total number of ratings for a given source.

        Args:
            source (Source): The source for which the rating count is being fetched.

        Returns:
            int: The total number of ratings.
        """
        return self.filter(source=source).count()

    def save_rating(self, user, source, rating: int):
        """
        Saves or updates the rating given by a user for a specific source.

        Args:
            user (User): The user giving the rating.
            source (Source): The source being rated.
            rating (int): The rating value being saved.
        """
        self.update_or_create(user=user, source=source, defaults={"rating": rating})

    def get_user_ratings_dict(self, user) -> Dict[int, int]:
        """
        Retrieves a dictionary of source ratings for a specific user.

        Args:
            user (User): The user whose ratings are being fetched.

        Returns:
            Dict[int, int]: A dictionary where the keys are source IDs and the values are the ratings.
        """
        ratings = self.filter(user=user).select_related("source")
        return {rating.source.pk: rating.rating for rating in ratings}
