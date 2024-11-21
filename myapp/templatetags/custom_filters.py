from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Filtro para acessar dicionário no template"""
    if dictionary is None:
        return None
    return dictionary.get(key, 0) 