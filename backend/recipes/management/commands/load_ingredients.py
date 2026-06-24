"""Command for loading ingredients from JSON."""

import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Load ingredients into the database."""

    def handle(self, *args, **kwargs):
        """Execute the command."""
        with open("/app/data/ingredients.json", encoding="utf-8") as f:
            ingredients_data = json.load(f)

        for ingredient in ingredients_data:
            Ingredient.objects.get_or_create(
                name=ingredient["name"],
                measurement_unit=ingredient["measurement_unit"],
            )

        self.stdout.write(
            self.style.SUCCESS("Ingredients loaded successfully")
        )
