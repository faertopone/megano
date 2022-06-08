from django import forms

from .models import UserReviews


class ReviewForm(forms.ModelForm):
    """ Форма для добавления комментария """
    class Meta:
        model = UserReviews
        exclude = ['product', 'client']
