"""Minimal Restaurant model (menu dependency; full profile lands later)."""

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel, unique_slug


class Restaurant(TimeStampedModel):
    """A food outlet. Owned by a user (typically role=restaurant_owner)."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="restaurants",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    logo_url = models.URLField(max_length=500, blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Restaurant, self.name, scope={}, instance=self)
        super().save(*args, **kwargs)
