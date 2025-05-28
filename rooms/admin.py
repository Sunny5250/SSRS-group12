from django.contrib import admin
from .models import StudyRoom, TimeSlot


@admin.register(StudyRoom)
class StudyRoomAdmin(admin.ModelAdmin):
    """自习室管理
    
    定义自习室在Django管理后台的展示和编辑方式。
    """
    # 列表页面显示的字段
    list_display = ('name', 'capacity', 'location', 'is_active', 'created_at')
    # 右侧过滤器选项
    list_filter = ('is_active', 'created_at', 'capacity')
    # 搜索字段配置
    search_fields = ('name', 'location', 'description')
    # 默认排序
    ordering = ('name',)
    # 只读字段，不可在编辑页面修改
    readonly_fields = ('created_at', 'updated_at')
    
    # 编辑页面的字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'capacity', 'location')
        }),
        ('详细信息', {
            'fields': ('equipment', 'image', 'is_active')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # 可折叠的分组
        }),
    )


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    """时间段管理
    
    定义时间段在Django管理后台的展示和编辑方式。
    """
    # 列表页面显示的字段
    list_display = ('name', 'start_time', 'end_time', 'is_active')
    # 右侧过滤器选项
    list_filter = ('is_active',)
    # 搜索字段配置
    search_fields = ('name',)
    # 默认排序
    ordering = ('start_time',)
