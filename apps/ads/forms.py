from django import forms

from .models import Ad, Review


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ("title", "description", "price", "location", "image", "category")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
