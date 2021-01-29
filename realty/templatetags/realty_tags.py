from django import template
from num2words import num2words

register = template.Library()


@register.filter(name='inwords')
def change_to_words(num):
    return num2words(num).title() + ' Naira Only'
