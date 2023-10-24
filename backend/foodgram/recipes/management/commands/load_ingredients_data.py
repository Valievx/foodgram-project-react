import csv

from django.core.management import BaseCommand
from recipes.models import Ingredients


class Command(BaseCommand):

    def handle(self, *args, **options):
        """ Загрузка ингредиентов в Базу Данных"""
        for data_object in csv.reader(
                open('./data/ingredients.csv', encoding="utf8")):
            ingredient = Ingredients(
                name=data_object[0],
                measurement_unit=data_object[1]
            )
            try:
                ingredient.save()
            except Exception as ex:
                print(ex)
        print('Upload successfully completed')
