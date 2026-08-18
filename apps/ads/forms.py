from django import forms

from .models import Ad, City, Review


class AdForm(forms.ModelForm):
    city = forms.CharField(
        required=False,
        label="Город",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "list": "city-list",
                "placeholder": "Выберите или введите город",
            }
        ),
    )

    class Meta:
        model = Ad
        fields = (
            "title",
            "description",
            "price",
            "deposit_amount",
            "city",
            "location",
            "image",
            "category",
            "size",
            "min_rental_days",
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например: Вечернее платье Zara",
                    "required": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Опишите товар подробно...",
                    "required": True,
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "1000",
                    "required": True,
                }
            ),
            "deposit_amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "5000"}
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "м. Тверская (необязательно)",
                }
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                    "required": True,
                }
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "size": forms.Select(attrs={"class": "form-select"}),
            "min_rental_days": forms.NumberInput(
                attrs={"class": "form-control", "min": "1"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # При редактировании показываем название города, а не его PK
        if self.instance and self.instance.pk and self.instance.city_id:
            self.initial["city"] = self.instance.city.name

    def clean_city(self):
        """Обработка города: если есть в базе - используем, иначе создаём."""
        city_name = (self.cleaned_data.get("city") or "").strip()
        if not city_name:
            return None

        # Поддержка числового PK (админка, тесты, legacy-формы)
        if city_name.isdigit():
            try:
                return City.objects.get(pk=int(city_name))
            except City.DoesNotExist:
                pass

        # Ищем существующий город (без учёта регистра)
        city = City.objects.filter(name__iexact=city_name).first()

        # Если город не найден - создаём новый
        if not city:
            city, _ = City.objects.get_or_create(name=city_name, region="")

        return city

    def clean_location(self):
        """Обработка района/метро: если пусто - подставляем 'Центральный'."""
        location = self.cleaned_data.get("location")

        # Если поле пустое или None - возвращаем значение по умолчанию
        if not location or not location.strip():
            return "Центральный"

        return location.strip()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
