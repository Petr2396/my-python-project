# accounts/templatetags/form_tags.py
from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    try:
        return field.as_widget(attrs={"class": css_class})
    except AttributeError:
        return field  # если передали строку