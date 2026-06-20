"""Filters for recipes API."""

import django_filters
from django_filters import ModelMultipleChoiceFilter
from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Filter recipes."""

    author = django_filters.NumberFilter(
        field_name='author__id'
    )

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )

    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        """Filter configuration."""

        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def filter_is_favorited(self, queryset, name, value):
        """Filter recipes by favorites."""
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none() if value else queryset

        if value:
            return queryset.filter(
                favorited_by__user=user
            )

        return queryset

    def filter_is_in_shopping_cart(
        self,
        queryset,
        name,
        value
    ):
        """Filter recipes by shopping cart."""
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none() if value else queryset

        if value:
            return queryset.filter(
                in_shopping_carts__user=user
            )

        return queryset
