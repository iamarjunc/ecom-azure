from django import template

register = template.Library()

@register.simple_tag(name = 'getstatus')
def getstatus(status):
    status = status - 1
    print(status)
    status_array = ['confirmed','processed', 'delivered','rejected']
    return status_array[status]