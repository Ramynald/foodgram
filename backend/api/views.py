"""API views."""

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarResponseSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeListSerializer,
                          RecipeMinifiedSerializer, SetAvatarSerializer,
                          SetPasswordSerializer, TagSerializer,
                          UserCreateSerializer, UserSerializer,
                          UserWithRecipesSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ingredients."""

    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """Return filtered ingredients queryset."""
        name = self.request.query_params.get("name")

        if name:
            return Ingredient.objects.filter(name__istartswith=name)

        return Ingredient.objects.all()


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet for users."""

    queryset = User.objects.all()

    def get_serializer_class(self):
        """Return serializer class for current action."""
        if self.action == "create":
            return UserCreateSerializer

        return UserSerializer

    def get_permissions(self):
        """Return permissions for current action."""
        if self.action in ["create", "list", "retrieve"]:
            return [AllowAny()]

        return [IsAuthenticated()]

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Return current user data."""
        serializer = UserSerializer(request.user, context={"request": request})

        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def set_password(self, request):
        """Change user password."""
        serializer = SetPasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]

        if not request.user.check_password(current_password):
            return Response(
                {"current_password": "Неверный текущий пароль."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(new_password)
        request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["put"], url_path="me/avatar")
    def avatar(self, request):
        """Upload user avatar."""
        serializer = SetAvatarSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        request.user.avatar = serializer.validated_data["avatar"]
        request.user.save()

        return Response(AvatarResponseSerializer(request.user).data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Delete user avatar."""
        request.user.avatar.delete(save=False)
        request.user.avatar = None
        request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        """Subscribe to an author."""
        author = get_object_or_404(User, pk=pk)

        if request.user == author:
            return Response(
                {"errors": "Нельзя подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Subscription.objects.filter(
            user=request.user, author=author
        ).exists():
            return Response(
                {"errors": "Вы уже подписаны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Subscription.objects.create(user=request.user, author=author)

        serializer = UserWithRecipesSerializer(
            author, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        """Unsubscribe from an author."""
        author = get_object_or_404(User, pk=pk)

        subscription = Subscription.objects.filter(
            user=request.user, author=author
        ).first()

        if subscription is None:
            return Response(
                {"errors": "Подписка не найдена"},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def subscriptions(self, request):
        """Return user subscriptions."""
        subscriptions = (
            Subscription.objects.filter(
                user=request.user,
            ).select_related("author")
        )

        authors = [sub.author for sub in subscriptions]

        page = self.paginate_queryset(authors)

        serializer = UserWithRecipesSerializer(
            page, many=True, context={"request": request}
        )

        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for recipes."""

    queryset = Recipe.objects.all().order_by("-id")
    serializer_class = RecipeCreateUpdateSerializer

    def get_serializer_class(self):
        """Return serializer class for current action."""
        if self.action in ["list", "retrieve"]:
            return RecipeListSerializer

        return super().get_serializer_class()

    permission_classes = [IsAuthorOrReadOnly]
    filterset_class = RecipeFilter

    @action(detail=True, methods=["post"])
    def favorite(self, request, pk=None):
        """Add recipe to favorites."""
        recipe = get_object_or_404(Recipe, pk=pk)

        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            return Response(
                {"errors": "Рецепт уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )

        Favorite.objects.create(user=request.user, recipe=recipe)

        serializer = RecipeMinifiedSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        """Remove recipe from favorites."""
        recipe = get_object_or_404(Recipe, pk=pk)

        favorite = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).first()

        if favorite is None:
            return Response(
                {"errors": "Рецепт не найден в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def shopping_cart(self, request, pk=None):
        """Add recipe to shopping cart."""
        recipe = get_object_or_404(Recipe, pk=pk)

        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                {"errors": "Рецепт уже в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ShoppingCart.objects.create(user=request.user, recipe=recipe)

        serializer = RecipeMinifiedSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        """Remove recipe from shopping cart."""
        recipe = get_object_or_404(Recipe, pk=pk)

        shopping_cart_item = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).first()

        if shopping_cart_item is None:
            return Response(
                {"errors": "Рецепт не найден в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shopping_cart_item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["get"],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Download shopping cart as a text file."""
        shopping_cart_items = ShoppingCart.objects.filter(
            user=request.user
        ).select_related("recipe")

        if not shopping_cart_items.exists():
            return Response(
                {"errors": "Список покупок пуст"},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe_ids = shopping_cart_items.values_list("recipe__id", flat=True)

        ingredients = (
            RecipeIngredient.objects.filter(recipe__id__in=recipe_ids)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
        )

        lines = [
            (
                f"{item['ingredient__name']} - "
                f"{item['total_amount']} "
                f"{item['ingredient__measurement_unit']}"
            )
            for item in ingredients
        ]

        response_content = "\n".join(lines)
        response = HttpResponse(response_content, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_cart.txt"'

        return response

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        """Return recipe link."""
        recipe = get_object_or_404(Recipe, pk=pk)

        short_link = request.build_absolute_uri(
            reverse("recipes-detail", args=[recipe.id])
        )

        return Response({"short-link": short_link})
