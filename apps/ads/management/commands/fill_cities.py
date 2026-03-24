"""
Management-команда для наполнения базы данных городами.
"""

from django.core.management.base import BaseCommand

from apps.ads.models import City

CITIES = [
    {"name": "Москва", "region": "Москва"},
    {"name": "Санкт-Петербург", "region": "Санкт-Петербург"},
    {"name": "Казань", "region": "Республика Татарстан"},
    {"name": "Новосибирск", "region": "Новосибирская область"},
    {"name": "Екатеринбург", "region": "Свердловская область"},
    {"name": "Краснодар", "region": "Краснодарский край"},
    {"name": "Нижний Новгород", "region": "Нижегородская область"},
    {"name": "Ростов-на-Дону", "region": "Ростовская область"},
    {"name": "Сочи", "region": "Краснодарский край"},
    {"name": "Владивосток", "region": "Приморский край"},
]


class Command(BaseCommand):
    """
    Команда для создания городов.

    Пример использования:
        python manage.py fill_cities
    """

    help = "Наполняет базу данных городами"

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for city_data in CITIES:
            city, created = City.objects.get_or_create(
                name=city_data["name"],
                defaults={"region": city_data["region"]},
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Создан город: {city}")
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"⊕ Пропущен город: {city}")
                )
                skipped_count += 1

        self.stdout.write("\n" + "=" * 40)
        self.stdout.write(self.style.SUCCESS("Готово!"))
        self.stdout.write(f"Создано: {created_count}")
        self.stdout.write(f"Пропущено: {skipped_count}")
        self.stdout.write(f"Всего городов: {City.objects.count()}")
