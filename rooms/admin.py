from django.contrib import admin
from .models import StudyRoom, TimeSlot


@admin.register(StudyRoom)
class StudyRoomAdmin(admin.ModelAdmin):
    """自习室管理"""
    list_display = ('name', 'capacity', 'location', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'capacity')
    search_fields = ('name', 'location', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'capacity', 'location')
        }),
        ('详细信息', {
            'fields': ('equipment', 'image', 'is_active')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    """时间段管理"""
    list_display = ('name', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('start_time',)
