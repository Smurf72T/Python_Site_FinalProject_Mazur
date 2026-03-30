from django import forms

from .models import Ad, City, Review


class AdForm(forms.ModelForm):
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
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Например: Вечернее платье Zara", "required": True}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Опишите товар подробно...", "required": True}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "1000", "required": True}),
            "deposit_amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": "5000"}),
            "city": forms.Select(attrs={"class": "form-select"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "м. Тверская (необязательно)"}),
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*", "required": True}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "size": forms.Select(attrs={"class": "form-select"}),
            "min_rental_days": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Загружаем активные города
        self.fields["city"].queryset = City.objects.filter(is_active=True)
        self.fields["city"].empty_label = None
        # Меняем виджет на TextInput для datalist
        self.fields["city"].widget = forms.TextInput(attrs={
            "class": "form-control",
            "list": "city-list",
            "placeholder": "Выберите или введите город"
        })

    def clean_city(self):
        """Обработка города: если есть в базе - используем, иначе создаём новый."""
        city_data = self.cleaned_data.get("city")

        # Если city_data это строка (название города)
        if isinstance(city_data, str):
            city_name = city_data.strip()
            if not city_name:
                return None

            # Ищем существующий город (без учёта регистра)
            city = City.objects.filter(name__iexact=city_name).first()

            # Если город не найден - создаём новый
            if not city:
                city = City.objects.create(name=city_name, region="")

            return city

        return city_data

    def clean_location(self):
        """Обработка района/метро: если не заполнено - подставляем 'Центральный'."""
        location = self.cleaned_data.get("location")
        
        # Если поле пустое или None - возвращаем значение по умолчанию
        if not location or not location.strip():
            return "Центральный"
        
        return location.strip()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
