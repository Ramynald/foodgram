from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from .serializers import (TagSerializer,
                          IngredientSerializer,
                          UserSerializer,
                          UserCreateSerializer,
                          SetPasswordSerializer,
                          SetAvatarSerializer,
                          AvatarResponseSerializer,
                          UserWithRecipesSerializer)
from recipes.models import Tag, Ingredient
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
            authors,
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(
            serializer.data
        )