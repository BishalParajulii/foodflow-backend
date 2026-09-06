"""Shared model utilities: timestamp base + scoped unique slugs."""

from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    """Abstract base with created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def unique_slug(model_cls, value, *, scope, instance=None, max_length=120):
    """Return a slug for ``value`` unique within ``scope`` (field lookups).

    Example: ``unique_slug(Category, "Momo", scope={"restaurant": r})``.
    Appends ``-2``, ``-3`` … on collision. ``instance`` excludes itself
    (for updates).
    """
    base = (slugify(value) or "item")[:max_length]
    slug = base
    counter = 2
    queryset = model_cls.objects.all()
    if instance is not None and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    while queryset.filter(slug=slug, **scope).exists():
        suffix = f"-{counter}"
        slug = f"{base[: max_length - len(suffix)]}{suffix}"
        counter += 1
    return slug
