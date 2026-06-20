"""Admin configuration for recipes."""

from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin configuration for ingredients."""

    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for tags."""

    list_display = (
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin configuration for recipes."""

    list_display = (
        'name',
        'author',
        'favorites_count',
    )
    search_fields = (
        'name',
        'author__username',
    )
    list_filter = (
        'tags',
    )

    def favorites_count(self, obj):
        """Return number of favorites."""
        return obj.favorited_by.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Admin configuration for recipe ingredients."""

    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = (
        'recipe__name',
        'ingredient__name',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin configuration for favorites."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user__username',
        'recipe__name',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin configuration for shopping cart."""

    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user__username',
        'recipe__name',
    )
