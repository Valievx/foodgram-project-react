import django_filters as filter
from recipes.models import Recipes, Tag


class RecipeFilter(filter.FilterSet):
    author = filter.CharFilter()
    tags = filter.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filter.NumberFilter(method='get_favorite')
    is_in_shopping_cart = filter.NumberFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipes
        fields = [
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_favorite(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(carts__user=self.request.user)
        return queryset


class IngredientFilter(filter.FilterSet):
    name = filter.CharFilter(
        field_name='name',
        lookup_expr='startswith')
