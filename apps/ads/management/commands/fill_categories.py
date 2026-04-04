"""
Management-команда для наполнения базы данных категориями одежды.
"""

from django.core.management.base import BaseCommand

from apps.ads.models import Category

CATEGORIES = [
    {
        "name": "Платья",
        "description": "Вечерние, коктейльные, повседневные платья",
    },
    {"name": "Костюмы", "description": "Деловые и вечерние костюмы"},
    {
        "name": "Верхняя одежда",
        "description": "Пальто, куртки, плащи, пиджаки",
    },
    {"name": "Обувь", "description": "Туфли, ботинки, сапоги, кроссовки"},
    {"name": "Аксессуары", "description": "Сумки, ремни, шарфы, украшения"},
    {"name": "Джинсы", "description": "Джинсы всех фасонов"},
    {
        "name": "Футболки и топы",
        "description": "Футболки, майки, топы, блузки",
    },
    {"name": "Свитера и кардиганы", "description": "Вязаная одежда"},
    {"name": "Юбки", "description": "Юбки различной длины и фасонов"},
    {"name": "Брюки и шорты", "description": "Брюки, джинсы, шорты"},
    {
        "name": "Спортивная одежда",
        "description": "Одежда для спорта и активного отдыха",
    },
    {"name": "Нижнее белье", "description": "Бельё и домашняя одежда"},
    {"name": "Головные уборы", "description": "Шапки, кепки, шляпы"},
    {"name": "Детская одежда", "description": "Одежда для детей"},
    {"name": "Другое", "description": "Прочие категории одежды"},
]


class Command(BaseCommand):
    """
    Команда для создания категорий одежды.

    Пример использования:
        python manage.py fill_categories
    """

    help = "Наполняет базу данных категориями одежды"

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for cat_data in CATEGORIES:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={"description": cat_data["description"]},
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Создана категория: {category.name}")
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⊕ Пропущена категория: {category.name}"
                    )
                )
                skipped_count += 1

        self.stdout.write("\n" + "=" * 40)
        self.stdout.write(self.style.SUCCESS("Готово!"))
        self.stdout.write(f"Создано: {created_count}")
        self.stdout.write(f"Пропущено: {skipped_count}")
        self.stdout.write(f"Всего категорий: {Category.objects.count()}")
