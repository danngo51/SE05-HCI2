from django import template

register = template.Library()

@register.filter
def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours} hr {mins} min"
    return f"{mins} min"
