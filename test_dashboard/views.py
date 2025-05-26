from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages

from .models import TestRun, TestResult
from .test_manager import TestManager


def is_admin(user):
    """检查用户是否是管理员"""
    return user.is_authenticated and (user.user_type == 'admin' or user.is_superuser)


def dashboard(request):
    """测试仪表板 - 移除了登录和权限检查，方便直接访问"""
    recent_runs = TestRun.objects.all()[:10]
    return render(request, 'test_dashboard/dashboard.html', {
        'recent_runs': recent_runs,
        'test_types': dict(TestRun.TEST_TYPE_CHOICES),
    })


def run_tests_view(request):
    """运行测试的视图 - 移除了登录和权限检查，方便直接访问"""
    if request.method == 'POST':
        test_type = request.POST.get('test_type', 'all')
        
        # 创建测试运行记录
        test_run = TestRun.objects.create(test_type=test_type)
        
        # 异步执行测试
        TestManager.run_tests_async(test_run)
        
        # 重定向到测试详情页
        return redirect('tests:test_detail', test_id=test_run.id)
    
    # GET请求直接返回仪表板
    return redirect('tests:dashboard')


def test_detail(request, test_id):
    """测试详情页 - 移除了登录和权限检查，方便直接访问"""
    test_run = get_object_or_404(TestRun, pk=test_id)
    results = TestResult.objects.filter(test_run=test_run)
    
    return render(request, 'test_dashboard/test_detail.html', {
        'test_run': test_run,
        'results': results,
        'test_types': dict(TestRun.TEST_TYPE_CHOICES),
        'result_data': test_run.get_result_data(),
    })


def test_progress(request, test_id):
    """获取测试进度的AJAX端点 - 移除了登录和权限检查，方便直接访问"""
    test_run = get_object_or_404(TestRun, pk=test_id)
    
    data = {
        'id': test_run.id,
        'status': test_run.status,
        'progress': test_run.progress,
        'test_type': test_run.test_type,
        'test_type_display': test_run.get_test_type_display(),
        'started_at': test_run.started_at.strftime('%Y-%m-%d %H:%M:%S'),
        'completed': test_run.status in ['completed', 'failed'],
        'success_rate': test_run.success_rate,
    }
    
    if test_run.completed_at:
        data['completed_at'] = test_run.completed_at.strftime('%Y-%m-%d %H:%M:%S')
    
    return JsonResponse(data)


def test_results(request, test_id):
    """获取测试结果的AJAX端点 - 移除了登录和权限检查，方便直接访问"""
    test_run = get_object_or_404(TestRun, pk=test_id)
    results = TestResult.objects.filter(test_run=test_run)
    
    data = {
        'test_run': {
            'id': test_run.id,
            'status': test_run.status,
            'progress': test_run.progress,
            'test_type': test_run.test_type,
            'test_type_display': test_run.get_test_type_display(),
            'started_at': test_run.started_at.strftime('%Y-%m-%d %H:%M:%S'),
            'success_rate': test_run.success_rate,
        },
        'results': []
    }
    
    if test_run.completed_at:
        data['test_run']['completed_at'] = test_run.completed_at.strftime('%Y-%m-%d %H:%M:%S')
    
    for result in results:
        data['results'].append({
            'id': result.id,
            'test_name': result.test_name,
            'status': result.status,
            'duration': result.duration,
            'created_at': result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse(data)
