from rest_framework import viewsets

from .serializers import TagSerializer, IngredientSerializer, UserSerializer
from recipes.models import Tag, Ingredient
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        name = self.request.query_params.get('name')

        if name:
            return Ingredient.objects.filter(
                name__istartswith=name
            )

        return Ingredient.objects.all()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer