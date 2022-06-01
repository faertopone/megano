import django_filters
from django import forms


class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "forms/widgets/multiple_input.html"
    option_template_name = "forms/widgets/input_option.html"


class CustomTextInput(forms.TextInput):
    template_name = "forms/widgets/text.html"


class CustomRangeWidget(django_filters.widgets.RangeWidget):
    template_name = "forms/widgets/multiwidget.html"
