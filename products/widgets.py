from django import forms


class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "forms/widgets/multiple_input.html"
    option_template_name = "forms/widgets/input_option.html"
