"""
Скрипт инициализации данных.
Заполняет базу данных начальными данными при первом запуске.
Запускается через: python manage.py shell < scripts/init_data.py
"""
from django.contrib.auth import get_user_model

User = get_user_model()

def init_data():
    """Создание суперпользователя по умолчанию (если не существует)."""
    
    # Создание тестового суперпользователя
    admin_username = 'admin'
    admin_email = 'admin@example.com'
    
    if not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password='admin123',
        )
        print(f"Created superuser: {admin_username} / admin123")
    else:
        print(f"Superuser {admin_username} already exists")

init_data()
print("Data initialization completed!")
