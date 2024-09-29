from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import MinLengthValidator, MaxLengthValidator

from apps.list.managers import ListManager
from apps.source.models import Source
from apps.article.models import Article

User = get_user_model()


class List(models.Model):
    """
    Represents a list of articles with associated metadata.

    This model stores information about the lists created by users,
    including the list's name, creator, related sources, articles,
    and other attributes.
    """

    list_id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=30, validators=[MinLengthValidator(1), MaxLengthValidator(30)]
    )
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
    sources = models.ManyToManyField(Source, related_name="lists", blank=True)
    articles = models.ManyToManyField(Article, related_name="articles_list", blank=True)
    main = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)

    objects = ListManager()

    def get_absolute_url(self) -> str:
        """
        Returns the absolute URL for the list details page.

        Returns:
            str: The URL path for the list details, constructed using the list_id.
        """
        return reverse("list:list-details", kwargs={"list_id": self.list_id})

    def __str__(self) -> str:
        """
        Returns a string representation of the list.

        Returns:
            str: The name of the list.
        """
        return self.name
