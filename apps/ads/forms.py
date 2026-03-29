from django import forms

from .models import Ad, Review


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = (
            "title",
            "description",
            "price",
            "deposit_amount",
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
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Москва, м. Тверская", "required": True}),
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/*", "required": True}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "size": forms.Select(attrs={"class": "form-select"}),
            "min_rental_days": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
