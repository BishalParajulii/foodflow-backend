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


class Branch(TimeStampedModel):
    """A physical outlet of a restaurant chain. Managed by owner/admins only."""

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="branches"
    )
    name = models.CharField(max_length=200, help_text='e.g. "Thamel Outlet"')
    slug = models.SlugField(max_length=120, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "slug"], name="uniq_branch_slug_per_restaurant"
            )
        ]

    def __str__(self) -> str:
        return f"{self.restaurant.name} / {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(
                Branch, self.name, scope={"restaurant": self.restaurant}, instance=self
            )
        super().save(*args, **kwargs)
