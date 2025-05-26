from django.db import models
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError


class StudyRoom(models.Model):
    """自习室模型"""
    name = models.CharField(max_length=100, verbose_name='自习室名称')
    description = models.TextField(blank=True, verbose_name='描述')
    capacity = models.PositiveIntegerField(verbose_name='容量')
    location = models.CharField(max_length=200, verbose_name='位置')
    equipment = models.TextField(blank=True, verbose_name='设备')
    image = models.ImageField(
        upload_to='room_images/',
        blank=True,
        null=True,
        verbose_name='图片'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '自习室'
        verbose_name_plural = '自习室'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    """时间段模型"""
    name = models.CharField(max_length=50, verbose_name='时间段名称')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    class Meta:
        verbose_name = '时间段'
        verbose_name_plural = '时间段'
        ordering = ['start_time']
    
    def clean(self):
        """验证时间段规则"""
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('结束时间必须晚于开始时间')
    
    def __str__(self):
        return f"{self.name} ({self.start_time}-{self.end_time})"
