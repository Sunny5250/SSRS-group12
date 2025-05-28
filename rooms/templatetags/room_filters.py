from django import template

# 创建模板过滤器和标签的注册器
register = template.Library()

@register.filter(name='split')
def split_string(value, arg):
    """
    将字符串按指定分隔符分割为列表
    
    用于在模板中将字符串按指定字符分割成列表，方便遍历。
    
    Args:
        value: 要分割的字符串
        arg: 分割字符，如逗号、空格等
    
    Returns:
        分割后的列表，如果输入不是字符串则返回原值
    
    使用方式: 
        {{ some_string|split:"," }}
    
    示例:
        输入: "apple,banana,orange"|split:","
        输出: ['apple', 'banana', 'orange']
    """
    if isinstance(value, str):
        return value.split(arg)
    return value
