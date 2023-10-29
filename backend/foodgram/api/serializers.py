from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import CustomUser, Subscription
from recipes.models import (Recipes, Tag,
                            Ingredients, RecipeTag,
                            RecipeIngredient, Favorite)


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериалайзер создания кастомного юзера """
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]


class CustomUserSerializer(UserSerializer):
    """ Сериалайзер кастомного юзера """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели Тег """
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор Ингредиента """
    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializers(serializers.ModelSerializer):
    """ Сериализатор Ингредиента в Рецепте """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор Рецепта """
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True, method_name='get_is_in_shopping_cart')
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializers(ingredients, many=True).data

    def get_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        return user.is_authenticated and recipe.carts.filter(
            user=user).exists()


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор добавления Ингредиента"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/обновления рецепта"""
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Должен быть указан хотя бы один Ингредиент')

        list_ingredients = []
        for i in ingredients:
            amount = i['amount']
            if int(amount) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0!')
            if i['id'] in list_ingredients:
                raise serializers.ValidationError(
                    'Рецепт не может иметь одинаковые Ингредиенты')
            list_ingredients.append(i['id'])

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Должен быть указан хотя бы один Тег')

        list_tags = []
        for tag in tags:
            if tag in list_tags:
                raise serializers.ValidationError(
                    'Не может быть выбрано 2 одинаковых тега')
            list_tags.append(tag)

        if not data.get('image'):
            raise serializers.ValidationError('Добавьте изображение')

        return data

    def create_tags(self, tags, recipe):
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

    def create_ingredients(self, ingredients, recipe):
        for i in ingredients:
            ingredient = Ingredients.objects.get(id=i['id'])
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=recipe, amount=i['amount'])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipes.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(ingredients, instance)
        RecipeTag.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        self.create_tags(tags, instance)
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image'):
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class ShowFavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения избранного. """

    class Meta:
        model = Recipes
        fields = ['id', 'name', 'image', 'cooking_time']


class ShowSubscribeSerializer(serializers.ModelSerializer):
    """ Сериализатор отображения подписки """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipes.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return ShowFavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj).count()


class SubscribeSerializer(serializers.ModelSerializer):
    """ Сериализатор подписки """
    class Meta:
        model = Subscription
        fields = '__all__'
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
            ),
        )

    def validate(self, data):
        if data['author'] == self.context['request'].user:
            raise serializers.ValidationError(
                'Невозможно оформить подписку на самого себя!')
        return data

    def to_representation(self, instance):
        return ShowSubscribeSerializer(instance.author, context={
            'request': self.context.get('request')
        }).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """ Сериализатор Корзины Покупок """
    class Meta:
        model = Recipes
        fields = ['id', 'name', 'image', 'cooking_time']


class FavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор Избранного"""
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']
