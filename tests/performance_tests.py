"""
系统性能测试
"""
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone
from django.db import connection
from django.test.client import Client
from datetime import datetime, date, timedelta
import time
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.base import BaseTestCase, TestDataFactory


class DatabasePerformanceTest(BaseTestCase):
    """数据库性能测试"""
    
    def test_room_list_query_performance(self):
        """测试自习室列表查询性能"""
        # 创建大量自习室数据
        for i in range(100):
            TestDataFactory.create_room(f'自习室{i}')
        
        self.login_student()
        
        # 测量查询时间
        start_time = time.time()
        response = self.client.get(reverse('rooms:room_list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        
        # 查询时间应该在合理范围内（例如小于2秒）
        query_time = end_time - start_time
        self.assertLess(query_time, 2.0, f"查询时间过长: {query_time}秒")
        
        # 检查数据库查询次数
        with self.assertNumQueries(lessThan=10):
            self.client.get(reverse('rooms:room_list'))
    
    def test_booking_list_query_performance(self):
        """测试预约列表查询性能"""
        # 创建大量预约数据
        for i in range(50):
            self.create_test_booking(
                user=self.student_user,
                booking_date=timezone.now().date() + timedelta(days=i % 30)
            )
        
        self.login_student()
        
        # 测量查询时间
        start_time = time.time()
        response = self.client.get(reverse('bookings:booking_list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        
        # 查询时间应该在合理范围内
        query_time = end_time - start_time
        self.assertLess(query_time, 1.5, f"预约列表查询时间过长: {query_time}秒")
    
    def test_admin_booking_list_performance(self):
        """测试管理员预约列表性能"""
        # 创建多个用户和大量预约
        users = []
        for i in range(10):
            user = TestDataFactory.create_user(f'user{i}')
            users.append(user)
        
        for user in users:
            for j in range(20):
                self.create_test_booking(
                    user=user,
                    booking_date=timezone.now().date() + timedelta(days=j % 30)
                )
        
        self.login_admin()
        
        # 测量查询时间
        start_time = time.time()
        response = self.client.get(reverse('bookings:admin_booking_list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        
        query_time = end_time - start_time
        self.assertLess(query_time, 3.0, f"管理员预约列表查询时间过长: {query_time}秒")


class ConcurrencyTest(TransactionTestCase):
    """并发测试"""
    
    def setUp(self):
        """设置测试数据"""
        super().setUp()
        # 重新创建基础数据（TransactionTestCase 不保留数据）
        self.student_user = TestDataFactory.create_user('student1', user_type='student')
        self.teacher_user = TestDataFactory.create_user('teacher1', user_type='teacher')
        self.room1 = TestDataFactory.create_room('101自习室')
        self.slot_morning = TestDataFactory.create_time_slot('上午', 8, 12)
    
    def test_concurrent_booking_creation(self):
        """测试并发预约创建"""
        booking_date = timezone.now().date() + timedelta(days=1)
        
        # 模拟两个用户同时预约同一时间段
        client1 = Client()
        client2 = Client()
        
        # 用户1登录
        client1.login(username='student1', password='testpass123')
        
        # 用户2登录  
        client2.login(username='teacher1', password='testpass123')
        
        # 同时发送预约请求
        response1 = client1.post(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}), {
            'time_slot': self.slot_morning.pk,
            'date': booking_date.strftime('%Y-%m-%d'),
            'purpose': '用户1的预约',
            'participants': 1
        })
        
        response2 = client2.post(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}), {
            'time_slot': self.slot_morning.pk,
            'date': booking_date.strftime('%Y-%m-%d'),
            'purpose': '用户2的预约',
            'participants': 1
        })
        
        # 验证只有一个预约成功
        from bookings.models import Booking
        successful_bookings = Booking.objects.filter(
            room=self.room1,
            time_slot=self.slot_morning,
            date=booking_date
        ).count()
        
        self.assertEqual(successful_bookings, 1, "应该只有一个预约成功")
        
        # 至少有一个响应是成功的重定向
        success_responses = [r for r in [response1, response2] if r.status_code == 302]
        self.assertGreaterEqual(len(success_responses), 1, "至少应该有一个成功的响应")


class LoadTest(BaseTestCase):
    """负载测试"""
    
    def test_multiple_users_browsing(self):
        """测试多用户同时浏览"""
        # 创建多个用户
        users = []
        for i in range(5):
            user = TestDataFactory.create_user(f'loadtest_user{i}')
            users.append(user)
        
        # 模拟多个用户同时访问系统
        clients = []
        for user in users:
            client = Client()
            client.login(username=user.username, password='testpass123')
            clients.append(client)
        
        # 测量响应时间
        start_time = time.time()
        
        responses = []
        for client in clients:
            # 每个用户访问自习室列表
            response = client.get(reverse('rooms:room_list'))
            responses.append(response)
        
        end_time = time.time()
        
        # 验证所有响应都成功
        for response in responses:
            self.assertEqual(response.status_code, 200)
        
        # 总响应时间应该在合理范围内
        total_time = end_time - start_time
        self.assertLess(total_time, 5.0, f"多用户访问总时间过长: {total_time}秒")
    
    def test_rapid_booking_operations(self):
        """测试快速预约操作"""
        self.login_student()
        
        # 快速创建多个预约
        start_time = time.time()
        
        for i in range(5):
            booking_date = timezone.now().date() + timedelta(days=i+1)
            response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}), {
                'time_slot': self.slot_morning.pk,
                'date': booking_date.strftime('%Y-%m-%d'),
                'purpose': f'快速预约{i+1}',
                'participants': 1
            })
            
            # 某些预约可能因为其他原因失败，但不应该因为性能问题而超时
            self.assertIn(response.status_code, [200, 302])
        
        end_time = time.time()
        
        operation_time = end_time - start_time
        self.assertLess(operation_time, 10.0, f"快速预约操作时间过长: {operation_time}秒")


class MemoryUsageTest(BaseTestCase):
    """内存使用测试"""
    
    def test_large_dataset_memory_usage(self):
        """测试大数据集的内存使用"""
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量数据
        for i in range(200):
            TestDataFactory.create_room(f'大数据测试室{i}')
        
        for i in range(100):
            self.create_test_booking(
                user=self.student_user,
                booking_date=timezone.now().date() + timedelta(days=i % 30)
            )
        
        # 执行查询操作
        self.login_student()
        self.client.get(reverse('rooms:room_list'))
        self.client.get(reverse('bookings:booking_list'))
        
        # 检查内存使用
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该在合理范围内（例如小于100MB）
        self.assertLess(memory_increase, 100, f"内存使用增长过多: {memory_increase}MB")


class CachePerformanceTest(BaseTestCase):
    """缓存性能测试"""
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
        }
    })
    def test_cached_room_list_performance(self):
        """测试缓存的自习室列表性能"""
        # 这里可以添加缓存相关的测试
        # 如果系统使用了缓存机制的话
        pass
    
    def test_repeated_queries_performance(self):
        """测试重复查询性能"""
        self.login_student()
        
        # 第一次查询
        start_time = time.time()
        response1 = self.client.get(reverse('rooms:room_list'))
        first_query_time = time.time() - start_time
        
        # 第二次查询（应该更快，如果有缓存的话）
        start_time = time.time()
        response2 = self.client.get(reverse('rooms:room_list'))
        second_query_time = time.time() - start_time
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # 如果没有缓存，第二次查询时间也应该在合理范围内
        self.assertLess(second_query_time, 2.0)


class ResponseTimeTest(BaseTestCase):
    """响应时间测试"""
    
    def test_page_response_times(self):
        """测试各页面响应时间"""
        self.login_student()
        
        pages_to_test = [
            ('rooms:room_list', {}),
            ('rooms:room_detail', {'pk': self.room1.pk}),
            ('bookings:booking_list', {}),
            ('bookings:booking_create', {'room_id': self.room1.pk}),
            ('accounts:profile', {}),
        ]
        
        for url_name, kwargs in pages_to_test:
            start_time = time.time()
            response = self.client.get(reverse(url_name, kwargs=kwargs))
            end_time = time.time()
            
            response_time = end_time - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time, 1.0, 
                          f"页面 {url_name} 响应时间过长: {response_time}秒")
    
    def test_form_submission_response_times(self):
        """测试表单提交响应时间"""
        self.login_student()
        
        # 测试预约创建表单提交
        start_time = time.time()
        response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}), {
            'time_slot': self.slot_morning.pk,
            'date': (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'purpose': '性能测试预约',
            'participants': 1
        })
        end_time = time.time()
        
        submission_time = end_time - start_time
        
        self.assertIn(response.status_code, [200, 302])
        self.assertLess(submission_time, 2.0, f"表单提交时间过长: {submission_time}秒")
