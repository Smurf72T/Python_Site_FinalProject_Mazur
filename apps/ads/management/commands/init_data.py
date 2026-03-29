"""
Management-команда для инициализации данных при первом запуске.
Заполняет таблицы Categories и Cities, если они пустые.
"""

from django.core.management.base import BaseCommand

from apps.ads.management.commands.fill_categories import CATEGORIES
from apps.ads.management.commands.fill_cities import CITIES
from apps.ads.models import Category, City


class Command(BaseCommand):
    """
    Команда для инициализации данных.

    Пример использования:
        python manage.py init_data
    """

    help = "Инициализирует данные (категории и города), если таблицы пустые"

    def handle(self, *args, **options):
        self.stdout.write("=" * 40)
        self.stdout.write("Инициализация данных...")
        self.stdout.write("=" * 40)

        # Инициализация категорий
        count = Category.objects.count()
        if count == 0:
            self.stdout.write("\nТаблица категорий пуста. Заполняю...")
            for cat_data in CATEGORIES:
                Category.objects.get_or_create(
                    name=cat_data["name"],
                    defaults={"description": cat_data["description"]},
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Создано категорий: {Category.objects.count()}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Таблица категорий уже заполнена ({count} записей)"
                )
            )

        # Инициализация городов
        count = City.objects.count()
        if count == 0:
            self.stdout.write("\nТаблица городов пуста. Заполняю...")
            for city_data in CITIES:
                City.objects.get_or_create(
                    name=city_data["name"],
                    defaults={"region": city_data["region"]},
                )
            self.stdout.write(
                self.style.SUCCESS(f"✓ Создано городов: {City.objects.count()}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Таблица городов уже заполнена ({count} записей)")
            )

        self.stdout.write("\n" + "=" * 40)
        self.stdout.write(self.style.SUCCESS("Инициализация данных завершена!"))
        self.stdout.write("=" * 40)
