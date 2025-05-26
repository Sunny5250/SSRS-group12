from django.contrib import admin
from .models import TestRun, TestResult


class TestResultInline(admin.TabularInline):
    model = TestResult
    extra = 0
    readonly_fields = ('test_name', 'status', 'duration', 'output', 'error', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    list_display = ('test_type', 'status', 'progress', 'success_rate', 'started_at', 'completed_at')
    list_filter = ('test_type', 'status')
    search_fields = ('test_type', 'status')
    readonly_fields = ('test_type', 'started_at', 'completed_at', 'status', 'progress', 'result_data', 'success_rate')
    inlines = [TestResultInline]
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'status', 'duration', 'created_at')
    list_filter = ('status', 'test_run')
    search_fields = ('test_name', 'status')
    readonly_fields = ('test_run', 'test_name', 'status', 'duration', 'output', 'error', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
