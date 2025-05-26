from django import template

register = template.Library()

@register.filter(name='split')
def split_string(value, arg):
    """
    将字符串按指定分隔符分割为列表
    使用方式: {{ some_string|split:"," }}
    """
    if isinstance(value, str):
        return value.split(arg)
    return value
