from django import forms

from products.models import Review


class ReviewForm(forms.ModelForm):
    """ Форма для добавления комментария """
    class Meta:
        model = Review
        exclude = ['product', 'client']
