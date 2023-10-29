from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()


class Ingredients(models.Model):
    """ Модель Ингредиентов """
    name = models.CharField(
        'Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель Тега"""
    name = models.CharField(
        'Название тэга',
        unique=True,
        max_length=200
    )
    color = models.CharField(
        'Цвет',
        unique=True,
        max_length=7,
    )
    slug = models.SlugField(
        'Slug',
        unique=True,
        max_length=200
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """ Модель Рецепта """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200
    )
    text = models.TextField(
        'Описание рецепта',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
    )
    pub_date = models.DateTimeField(
        'Время публикации',
        auto_now_add=True
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            1,
            message='Время приготовления не менее 1 минуты!'
        )]
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """ Связывающая модель Рецепта и Ингредиентов"""
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(9999),
            MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class RecipeTag(models.Model):
    """Связывающая модель Тега и Рецепта"""
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецептов'

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class Favorite(models.Model):
    """ Модель Избранного"""
    recipe = models.ForeignKey(
        Recipes,
        related_name='favorite',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name='favorite',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'user',
                ),
                name='unique_favorite',
            ),
        )

    def __str__(self):
        return f'{self.recipes.name}'


class ShoppingCart(models.Model):
    """ Модель Корзины Покупок"""
    recipe = models.ForeignKey(
        Recipes,
        related_name='carts',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        related_name='carts',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
