from django.contrib import admin

from users.models import Subscription
from recipes.models import (Ingredients, Recipes, Tag,
                            RecipeIngredient, RecipeTag)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = ['name']
    empty_value_display = '-пусто-'


class IngredientsInLine(admin.TabularInline):
    model = RecipeIngredient


class TagsInLine(admin.TabularInline):
    model = RecipeTag


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']
    search_fields = ['name']
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'slug']
    search_fields = ['name', 'slug']
    empty_value_display = '-пусто-'


@admin.register(Recipes)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'author']
    search_fields = ['name', 'author__username']
    list_filter = ['tags']
    empty_value_display = '-пусто-'

    inlines = (
        IngredientsInLine,
        TagsInLine
    )
