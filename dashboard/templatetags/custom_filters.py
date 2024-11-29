from django import template

register = template.Library()

@register.filter(name='split')
def split(value, delimiter):
    """
    Rozdziela ciąg znaków `value` na listę, używając `delimiter` jako separatora.
    """
    return value.split(delimiter)
