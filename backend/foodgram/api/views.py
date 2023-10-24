from rest_framework import viewsets, status
from rest_framework import filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend

from users.models import Subscription, CustomUser
from .permissions import IsAuthorOrAdminOrReadOnly
from .pagination import CustomPagination
from .filters import RecipeFilter
from recipes.models import (Ingredients, Recipes,
                            RecipeIngredient, Tag,
                            Favorite, ShoppingCart)
from .serializers import (RecipeSerializer, RecipeCreateSerializer,
                          IngredientSerializer, TagSerializer,
                          SubscribeSerializer, ShowSubscribeSerializer,
                          ShoppingCartSerializer, FavoriteSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    """ Отображение Ингредиентов """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ Отображение Тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Отображение Рецептов"""
    serializer_class = RecipeSerializer
    queryset = Recipes.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def request_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return RecipeCreateSerializer
        return RecipeSerializer


class SubscribeView(APIView):
    """ Подписка/Отписка """
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        author = get_object_or_404(CustomUser, id=id)
        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'author': id},
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            if not author:
                return Response({'Такого автора не существует'},
                                status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        author = get_object_or_404(CustomUser, id=id)
        if not Subscription.objects.filter(
                user=request.user,
                author=author
        ).exists():
            return Response(
                {'Вы не подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(
            user=request.user.id,
            author=id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShowSubscribeView(ListAPIView):
    """ Отображение подписок"""
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get(self, request):
        queryset = CustomUser.objects.filter(subscriber__author=request.user)
        page = self.paginate_queryset(queryset)
        serializer = ShowSubscribeSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class ShoppingCartViewSet(APIView):
    """ Добавление в корзину"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        recipe = get_object_or_404(Recipes, id=id)
        if ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).exists():
            return Response(
                {f'Рецепт "{recipe.name}" уже в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST)

        serializer = ShoppingCartSerializer(recipe)
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipes, id=id)
        if not ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe.id
        ).exists():
            return Response(
                {'Рецепт не был добавлен в корзину'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.get(
            user=request.user.id,
            recipe=recipe.id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(APIView):
    """ Добавление в Избранное """
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def post(self, request, id):
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': id},
            context={'request': request}
        )
        if Favorite.objects.filter(
            recipe_id=id,
            user_id=request.user.id
        ).exists():
            return Response(
                {'Рецепт уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not Favorite.objects.filter(
            recipe_id=id,
            user_id=request.user.id
        ).exists():
            return Response(
                {'Такого рецепта не существует'},
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipes, id=id)
        if not Favorite.objects.filter(
                user=request.user.id,
                recipe=recipe.id
        ).exists():
            return Response(
                {'Рецепт не был добавлен в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.get(
            user=request.user.id,
            recipe=recipe.id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def download_shopping_cart(request):
    """ Метод для скачивания списка покупок """
    shopping_list = []
    for obj in (RecipeIngredient.objects.filter(
            recipe__carts__user=request.user)
            .values('ingredient').annotate(Sum('amount'))
            .values_list('ingredient__name',
                         'ingredient__measurement_unit',
                         'amount__sum')):
        shopping_list.append(f'{obj[0]}\n{obj[2]} {obj[1]}\n-------\n')

    headers = {
        "Content-Type": "text/plain",
        "Content-Disposition": 'attachment; filename="shopping_cart_list.txt"'
    }
    return HttpResponse(shopping_list, headers)
