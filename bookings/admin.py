from django.contrib import admin
from .models import Booking, BookingHistory


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """预约管理"""
    list_display = ('user', 'room', 'date', 'time_slot', 'status', 'participants', 'created_at')
    list_filter = ('status', 'date', 'room', 'created_at')
    search_fields = ('user__username', 'room__name', 'purpose')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('预约信息', {
            'fields': ('user', 'room', 'time_slot', 'date', 'participants')
        }),
        ('详细信息', {
            'fields': ('purpose', 'status')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """根据用户类型过滤数据"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.user_type == 'admin':
            return qs
        else:
            return qs.filter(user=request.user)
    
    def has_change_permission(self, request, obj=None):
        """权限控制"""
        if obj is None:
            return True
        if request.user.is_superuser or request.user.user_type == 'admin':
            return True
        return obj.user == request.user and obj.status == 'pending'


@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    """预约历史管理"""
    list_display = ('booking', 'action', 'operator', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('booking__user__username', 'operator__username', 'notes')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
