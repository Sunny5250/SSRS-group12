from django.apps import AppConfig


class RoomsConfig(AppConfig):
    """自习室应用配置
    
    Django应用配置类，定义自习室应用的基本设置。
    """
    # 使用BigAutoField作为主键字段类型
    default_auto_field = "django.db.models.BigAutoField"
    # 应用名称
    name = "rooms"
