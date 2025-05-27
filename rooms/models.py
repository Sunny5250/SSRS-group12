from django.db import models
from django.core.exceptions import ValidationError


class StudyRoom(models.Model):
    """自习室模型
    
    定义自习室的基本属性，如名称、容量、位置等信息。
    用于记录系统中可供预约的自习室信息。
    """
    name = models.CharField(max_length=100, verbose_name='自习室名称')  # 自习室名称，如"101自习室"
    description = models.TextField(blank=True, verbose_name='描述')  # 自习室的详细描述，可为空
    capacity = models.PositiveIntegerField(verbose_name='容量')  # 自习室可容纳的人数
    location = models.CharField(max_length=200, verbose_name='位置')  # 自习室位置，如"图书馆一楼A区"
    equipment = models.TextField(blank=True, verbose_name='设备')  # 自习室配备的设备描述，可为空
    image = models.ImageField(
        upload_to='room_images/',  # 图片存储路径
        blank=True,  # 允许为空
        null=True,  # 数据库中可为null
        verbose_name='图片'  # 自习室图片
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')  # 自习室是否可用，默认为启用
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')  # 记录创建时间，自动添加
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')  # 记录更新时间，自动更新
    
    class Meta:
        """模型元数据选项"""
        verbose_name = '自习室'  # 后台显示的单数名称
        verbose_name_plural = '自习室'  # 后台显示的复数名称
        ordering = ['name']  # 默认排序字段
    
    def __str__(self):
        """返回自习室名称作为对象的字符串表示"""
        return self.name


class TimeSlot(models.Model):
    """时间段模型
    
    定义可预约的时间段，如上午、下午、晚上等。
    用于设置自习室可预约的时间范围。
    """
    name = models.CharField(max_length=50, verbose_name='时间段名称')  # 时间段名称，如"上午""下午"
    start_time = models.TimeField(verbose_name='开始时间')  # 时间段开始时间
    end_time = models.TimeField(verbose_name='结束时间')  # 时间段结束时间
    is_active = models.BooleanField(default=True, verbose_name='是否启用')  # 时间段是否可用，默认为启用
    
    class Meta:
        """模型元数据选项"""
        verbose_name = '时间段'  # 后台显示的单数名称
        verbose_name_plural = '时间段'  # 后台显示的复数名称
        ordering = ['start_time']  # 默认按开始时间排序
    
    def clean(self):
        """
        验证时间段规则
        确保结束时间晚于开始时间
        """
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('结束时间必须晚于开始时间')
    
    def __str__(self):
        """返回格式化的时间段信息作为对象的字符串表示"""
        return f"{self.name} ({self.start_time}-{self.end_time})"
