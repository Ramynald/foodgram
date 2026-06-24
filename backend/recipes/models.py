"""Models for recipes application."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

MAX_TAG_LENGTH = 32
MAX_INGREDIENT_LENGTH = 64
MAX_MEASUREMENT_UNIT_LENGTH = 16
MAX_RECIPE_NAME_LENGTH = 128

MIN_VALUE = 1
MAX_VALUE = 32000


class Tag(models.Model):
    """Recipe tag model."""

    name = models.CharField(
        max_length=MAX_TAG_LENGTH, unique=True
    )
    slug = models.SlugField(
        max_length=MAX_TAG_LENGTH, unique=True
    )

    def __str__(self):
        """Return tag name."""
        return self.name


class Ingredient(models.Model):
    """Ingredient model."""

    name = models.CharField(
        max_length=MAX_INGREDIENT_LENGTH, unique=True
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT_LENGTH
    )

    def __str__(self):
        """Return ingredient name."""
        return self.name


class Recipe(models.Model):
    """Recipe model."""

    author = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="recipes",
    )

    name = models.CharField(
        max_length=MAX_RECIPE_NAME_LENGTH
    )
    text = models.TextField()
    image = models.ImageField(upload_to="recipes/")
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE),
        ]
    )

    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
    )

    def __str__(self):
        """Return recipe name."""
        return self.name


class RecipeIngredient(models.Model):
    """Recipe ingredient model."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipes",
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE),
        ]
    )

    class Meta:
        """Model configuration."""

        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            ),
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="amount_gt_zero",
            ),
        ]

    def __str__(self):
        """Return ingredient amount representation."""
        return f"{self.ingredient} ({self.amount})"


class Favorite(models.Model):
    """Favorite recipe model."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )

    class Meta:
        """Model configuration."""

        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite",
            ),
        ]

    def __str__(self):
        """Return favorite representation."""
        return f"{self.user} - {self.recipe}"


class ShoppingCart(models.Model):
    """Shopping cart model."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="shopping_carts",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_carts",
    )

    class Meta:
        """Model configuration."""

        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_shopping_cart",
            ),
        ]

    def __str__(self):
        """Return shopping cart representation."""
        return f"{self.user} - {self.recipe}"
