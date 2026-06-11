from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Tag, Ingredient, Recipe
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.subscribers.filter(user=request.user).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True
    )
    new_password = serializers.CharField(
        write_only=True
    )

    def validate_new_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            return value
        raise serializers.ValidationError('New password must be different from the old one.')


class SetAvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField()


class AvatarResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('avatar',)


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request is None:
            return []

        recipes_limit = request.query_params.get('recipes_limit')
        recipes_qs = obj.recipes.all()

        if recipes_limit is not None and recipes_limit.isdigit():
            recipes_qs = recipes_qs[:int(recipes_limit)]

        return RecipeMinifiedSerializer(
            recipes_qs,
            many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()