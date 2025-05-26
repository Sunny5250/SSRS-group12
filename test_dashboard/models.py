from django.db import models
from django.utils import timezone
import json


class TestRun(models.Model):
    """测试运行记录"""
    TEST_TYPE_CHOICES = [
        ('all', '所有测试'),
        ('unit', '单元测试'),
        ('integration', '集成测试'),
        ('performance', '性能测试'),
        ('models', '模型测试'),
        ('views', '视图测试'),
        ('api', 'API测试'),
        ('coverage', '覆盖率测试'),
        ('lint', '代码检查'),
        ('security', '安全检查'),
        ('full', '完整测试'),
    ]

    STATUS_CHOICES = [
        ('queued', '排队中'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES, verbose_name='测试类型')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued', verbose_name='状态')
    progress = models.IntegerField(default=0, verbose_name='进度')
    result_data = models.TextField(blank=True, null=True, verbose_name='结果数据')
    success_rate = models.FloatField(default=0.0, verbose_name='成功率')
    
    def set_result_data(self, data):
        """设置结果数据"""
        self.result_data = json.dumps(data)
        self.save()
    
    def get_result_data(self):
        """获取结果数据"""
        if self.result_data:
            return json.loads(self.result_data)
        return {}
    
    def mark_as_complete(self, success_rate=0.0):
        """标记为已完成"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress = 100
        self.success_rate = success_rate
        self.save()
    
    def mark_as_failed(self):
        """标记为失败"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.save()
    
    def update_progress(self, progress):
        """更新进度"""
        self.progress = min(progress, 100)
        if self.progress == 100 and self.status == 'running':
            self.status = 'completed'
            self.completed_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.get_test_type_display()} - {self.started_at}"
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = '测试运行'
        verbose_name_plural = '测试运行'


class TestResult(models.Model):
    """测试结果详情"""
    test_run = models.ForeignKey(TestRun, on_delete=models.CASCADE, related_name='results', verbose_name='测试运行')
    test_name = models.CharField(max_length=255, verbose_name='测试名称')
    status = models.CharField(max_length=20, verbose_name='状态')
    duration = models.FloatField(default=0.0, verbose_name='耗时(秒)')
    output = models.TextField(blank=True, null=True, verbose_name='输出')
    error = models.TextField(blank=True, null=True, verbose_name='错误')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    def __str__(self):
        return f"{self.test_name} - {self.status}"
    
    class Meta:
        ordering = ['created_at']
        verbose_name = '测试结果'
        verbose_name_plural = '测试结果'
