import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        with open('../data/ingredients.json', encoding='utf-8') as f:
            ingredients_data = json.load(f)

        for ingredient in ingredients_data:
            Ingredient.objects.get_or_create(
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit'],
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Ingredients loaded successfully'
            )
        )