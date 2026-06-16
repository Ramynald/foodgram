from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.shortcuts import get_object_or_404

from .serializers import (TagSerializer,
                          IngredientSerializer,
                          UserSerializer,
                          UserCreateSerializer,
                          SetPasswordSerializer,
                          SetAvatarSerializer,
                          AvatarResponseSerializer,
                          UserWithRecipesSerializer,
                          RecipeListSerializer,
                          RecipeMinifiedSerializer,
                          RecipeCreateUpdateSerializer)
from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            Favorite,
                            ShoppingCart)
from users.models import User, Subscription 


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


class UserViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet
    ):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        if not request.user.check_password(current_password):
            return Response(
                {'current_password': 'Неверный текущий пароль.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(new_password)
        request.user.save()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar'
    )
    def avatar(self, request):
        serializer = SetAvatarSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        request.user.avatar = serializer.validated_data['avatar']
        request.user.save()

        return Response(
            AvatarResponseSerializer(request.user).data
        )
    
    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar.delete(save=False)
        request.user.avatar = None
        request.user.save()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(
        detail=True,
        methods=['post']
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(
            User,
            pk=pk
        )

        if request.user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Subscription.objects.filter(
            user=request.user,
            author=author
        ).exists():
            return Response(
                {'errors': 'Вы уже подписаны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        Subscription.objects.create(
            user=request.user,
            author=author
        )

        serializer = UserWithRecipesSerializer(
            author,
            context={'request': request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(
            User,
            pk=pk
        )

        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        ).first()

        if subscription is None:
            return Response(
                {'errors': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(
        detail=False,
        methods=['get']
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(
            user=request.user
        ).select_related('author')

        authors = [sub.author for sub in subscriptions]

        page = self.paginate_queryset(authors)

        serializer = UserWithRecipesSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(
            serializer.data
        )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateUpdateSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(
        detail=True,
        methods=['post']
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(
            Recipe,
            pk=pk
        )

        if Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            return Response(
                {'errors': 'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Favorite.objects.create(
            user=request.user,
            recipe=recipe
        )

        serializer = RecipeMinifiedSerializer(recipe)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        recipe = get_object_or_404(
            Recipe,
            pk=pk
        )

        favorite = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()

        if favorite is None:
            return Response(
                {'errors': 'Рецепт не найден в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        favorite.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=['post']
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(
            Recipe,
            pk=pk
        )

        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            return Response(
                {'errors': 'Рецепт уже в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ShoppingCart.objects.create(
            user=request.user,
            recipe=recipe
        )

        serializer = RecipeMinifiedSerializer(recipe)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(
            Recipe,
            pk=pk
        )

        shopping_cart_item = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()

        if shopping_cart_item is None:
            return Response(
                {'errors': 'Рецепт не найден в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_cart_item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )