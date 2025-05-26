from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理"""
    list_display = ('username', 'email', 'user_type', 'student_id', 'phone', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'student_id', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('user_type', 'phone', 'student_id', 'avatar'),
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('扩展信息', {
            'fields': ('user_type', 'phone', 'student_id'),
        }),
    )
