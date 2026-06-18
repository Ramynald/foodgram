from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


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


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.in_shopping_carts.filter(user=request.user).exists() 


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                'Это поле обязательно.'
            )
        return value

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                'Это поле обязательно.'
            )
        return value

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


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )

    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один ингредиент.'
            )

        ingredient_ids = [
            item['ingredient'].id for item in value
        ]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.'
            )

        return value
    
    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один тег.'
            )

        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными.'
            )

        return value
    
    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Изображение обязательно.'
            )
        return value
    
    def create_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'],
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        if ingredients_data is None:
            raise serializers.ValidationError(
                {'ingredients': 'Это поле обязательно.'}
            )

        if tags_data is None:
            raise serializers.ValidationError(
                {'tags': 'Это поле обязательно.'}
            )

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )

        recipe.tags.set(tags_data)

        self.create_ingredients(
            recipe,
            ingredients_data
        )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        if ingredients_data is None:
            raise serializers.ValidationError({
                'ingredients': 'Это поле обязательно.'
            })

        if tags_data is None:
            raise serializers.ValidationError({
                'tags': 'Это поле обязательно.'
            })

        instance.tags.set(tags_data)

        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(
            instance,
            ingredients_data
        )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context=self.context
        ).data