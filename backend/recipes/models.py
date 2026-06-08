from django.db import models
from django.db.models import Q


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(max_length=32, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=64, unique=True)
    measurement_unit = models.CharField(max_length=16)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(max_length=128)
    text = models.TextField()
    image = models.ImageField(upload_to='recipes/')
    cooking_time = models.PositiveIntegerField()

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
    )
    amount = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            ),
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name='amount_gt_zero',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient} ({self.amount})'


class Favorite(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='shopping_carts',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_carts',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
    