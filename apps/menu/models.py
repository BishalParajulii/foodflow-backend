"""Menu models: categories, items, modifier groups/options.

Structure: Restaurant -> Category -> MenuItem, with reusable ModifierGroups
(e.g. "Size", "Extra toppings") attached to items. ModifierGroups belong to
a restaurant so outlets share them across their items.
"""

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel, unique_slug
from apps.restaurants.models import Restaurant


class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, restaurant__is_active=True)


class Category(TimeStampedModel):
    """A grouping of items within a restaurant (e.g. "Momos", "Beverages")."""

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    objects = CategoryQuerySet.as_manager()

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "slug"], name="uniq_category_slug_per_restaurant"
            )
        ]

    def __str__(self) -> str:
        return f"{self.restaurant.name} / {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(
                Category, self.name, scope={"restaurant": self.restaurant}, instance=self
            )
        super().save(*args, **kwargs)


class MenuItemQuerySet(models.QuerySet):
    def available(self):
        return self.filter(
            is_available=True,
            category__is_active=True,
            category__restaurant__is_active=True,
        )


class MenuItem(TimeStampedModel):
    """A sellable dish/item on the menu."""

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Original price when discounted (must be >= price).",
    )
    image_url = models.URLField(max_length=500, blank=True, default="")
    is_veg = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    preparation_time_minutes = models.PositiveIntegerField(default=15)
    sort_order = models.PositiveIntegerField(default=0)
    modifier_groups = models.ManyToManyField(
        "ModifierGroup", blank=True, related_name="menu_items"
    )

    objects = MenuItemQuerySet.as_manager()

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"], name="uniq_item_slug_per_category"
            )
        ]

    def __str__(self) -> str:
        return f"{self.category.name} / {self.name}"

    @property
    def restaurant(self) -> Restaurant:
        return self.category.restaurant

    def clean(self):
        super().clean()
        if (
            self.compare_at_price is not None
            and self.price is not None
            and self.compare_at_price < self.price
        ):
            raise ValidationError(
                {"compare_at_price": "Compare-at price must be >= price."}
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(
                MenuItem, self.name, scope={"category": self.category}, instance=self
            )
        self.full_clean(exclude=["modifier_groups"], validate_unique=False)
        super().save(*args, **kwargs)


class ModifierGroup(TimeStampedModel):
    """A choice set attached to items (e.g. "Size": 1 required of 3)."""

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="modifier_groups"
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    min_select = models.PositiveIntegerField(
        default=0, help_text="0 = optional extras; >=1 = customer must choose."
    )
    max_select = models.PositiveIntegerField(default=1)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["restaurant", "name"], name="uniq_modifier_group_per_restaurant"
            )
        ]

    def __str__(self) -> str:
        return f"{self.restaurant.name} / {self.name}"

    def clean(self):
        super().clean()
        if self.max_select < 1:
            raise ValidationError({"max_select": "Must allow at least 1 selection."})
        if self.min_select > self.max_select:
            raise ValidationError(
                {"min_select": "Cannot exceed max_select."}
            )

    def save(self, *args, **kwargs):
        self.full_clean(validate_unique=False)
        super().save(*args, **kwargs)


class ModifierOption(TimeStampedModel):
    """One selectable option within a group (e.g. "Large" +Rs 60)."""

    group = models.ForeignKey(
        ModifierGroup, on_delete=models.CASCADE, related_name="options"
    )
    name = models.CharField(max_length=120)
    price_delta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Extra charge over the item price.",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["group", "name"], name="uniq_modifier_option_per_group"
            )
        ]

    def __str__(self) -> str:
        return f"{self.group.name} / {self.name}"

    @property
    def restaurant(self) -> Restaurant:
        return self.group.restaurant
