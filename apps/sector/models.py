from typing import Any

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class Sector(models.Model):
    """
    Model representing a sector.
    """

    sector_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ("name",)

    def save(self, *args: Any, **kwargs: Any):
        """
        Overrides the save method to automatically generate a slug
        from the sector's name before saving.

        Args:
            args (Any): Positional arguments passed to the save method.
            kwargs (Any): Keyword arguments passed to the save method.
        """
        self.slug = slugify(self.name)
        super(Sector, self).save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """
        Returns the URL for the sector details page.

        Returns:
            str: The URL for the sector details page.
        """
        return reverse("sector:sector-details", kwargs={"slug": self.slug})

    def __str__(self) -> str:
        """
        Returns a string representation of the sector.

        Returns:
            str: The name of the sector.
        """
        return self.name
