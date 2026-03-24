from django import template

register = template.Library()


@register.filter
def days_between(start_date, end_date):
    """
    Вычисляет количество дней между двумя датами (включительно).
    """
    if start_date and end_date:
        return (end_date - start_date).days + 1
    return 0
