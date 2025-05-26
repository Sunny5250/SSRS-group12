"""
系统集成测试
"""
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, date, timedelta
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.base import BaseTestCase, TestDataFactory

User = get_user_model()


class UserBookingIntegrationTest(BaseTestCase):
    """用户预约集成测试"""
    
    def test_complete_booking_flow(self):
        """测试完整的预约流程"""
        # 1. 用户注册
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'newuserpass123',
            'password2': 'newuserpass123',
            'user_type': 'student',
            'first_name': '新',
            'last_name': '用户'
        })
        self.assertEqual(response.status_code, 302)
        
        new_user = User.objects.get(username='newuser')
        
        # 2. 浏览自习室列表
        response = self.client.get(reverse('rooms:room_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room1.name)
        
        # 3. 查看自习室详情
        response = self.client.get(reverse('rooms:room_detail', kwargs={'pk': self.room1.pk}))
        self.assertEqual(response.status_code, 200)
        
        # 4. 创建预约
        booking_date = timezone.now().date() + timedelta(days=1)
        response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}), {
            'time_slot': self.slot_morning.pk,
            'date': booking_date.strftime('%Y-%m-%d'),
            'purpose': '学习编程',
            'participants': 1
        })
        self.assertEqual(response.status_code, 302)
        
        # 5. 查看预约列表
        response = self.client.get(reverse('bookings:booking_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '学习编程')
        
        # 6. 查看预约详情
        booking = new_user.booking_set.first()
        response = self.client.get(reverse('bookings:booking_detail', kwargs={'pk': booking.pk}))
        self.assertEqual(response.status_code, 200)
        
        # 7. 取消预约
        response = self.client.post(reverse('bookings:booking_cancel', kwargs={'pk': booking.pk}))
        self.assertEqual(response.status_code, 302)
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
    
    def test_admin_booking_management_flow(self):
        """测试管理员预约管理流程"""
        # 1. 学生创建预约
        booking = self.create_test_booking(user=self.student_user, status='pending')
        
        # 2. 管理员登录
        self.login_admin()
        
        # 3. 查看所有预约
        response = self.client.get(reverse('bookings:admin_booking_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(booking))
        
        # 4. 审批预约
        response = self.client.post(reverse('bookings:booking_approve', kwargs={'pk': booking.pk}), {
            'action': 'approve',
            'notes': '审批通过'
        })
        self.assertEqual(response.status_code, 302)
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        
        # 5. 查看预约历史
        response = self.client.get(reverse('bookings:booking_detail', kwargs={'pk': booking.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '审批通过')


class BookingConflictTest(BaseTestCase):
    """预约冲突测试"""
    
    def test_time_slot_conflict_prevention(self):
        """测试时间段冲突预防"""
        booking_date = timezone.now().date() + timedelta(days=1)
        
        # 第一个用户创建预约
        self.login_student()
        response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}), {
            'time_slot': self.slot_morning.pk,
            'date': booking_date.strftime('%Y-%m-%d'),
            'purpose': '学习数学',
            'participants': 1
        })
        self.assertEqual(response.status_code, 302)
        
        # 第二个用户尝试预约同一时间段
        self.login_teacher()
        response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}), {
            'time_slot': self.slot_morning.pk,
            'date': booking_date.strftime('%Y-%m-%d'),
            'purpose': '学习物理',
            'participants': 1
        })
        self.assertEqual(response.status_code, 200)  # 应该返回表单页面并显示错误
        
        # 验证只有一个预约被创建
        from bookings.models import Booking
        bookings = Booking.objects.filter(
            room=self.room1,
            time_slot=self.slot_morning,
            date=booking_date,
            status__in=['pending', 'confirmed']
        )
        self.assertEqual(bookings.count(), 1)
    
    def test_capacity_limit_enforcement(self):
        """测试容量限制执行"""
        # 使用小容量的房间
        small_room = TestDataFactory.create_room('小会议室', capacity=2)
        
        self.login_student()
        response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': small_room.pk}), {
            'time_slot': self.slot_morning.pk,
            'date': (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'purpose': '小组讨论',
            'participants': 5  # 超过容量
        })
        
        # 应该返回表单页面并显示错误
        self.assertEqual(response.status_code, 200)


class SystemWorkflowTest(BaseTestCase):
    """系统工作流程测试"""
    
    def test_daily_booking_workflow(self):
        """测试日常预约工作流程"""
        booking_date = timezone.now().date() + timedelta(days=1)
        
        # 1. 多个用户创建预约
        users = [self.student_user, self.teacher_user]
        time_slots = [self.slot_morning, self.slot_afternoon]
        rooms = [self.room1, self.room2]
        
        bookings = []
        for i, user in enumerate(users):
            self.login_user(user)
            response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': rooms[i].pk}), {
                'time_slot': time_slots[i].pk,
                'date': booking_date.strftime('%Y-%m-%d'),
                'purpose': f'用户{i+1}的预约',
                'participants': 1
            })
            self.assertEqual(response.status_code, 302)
            
            booking = user.booking_set.first()
            bookings.append(booking)
        
        # 2. 管理员批量处理预约
        self.login_admin()
        for booking in bookings:
            response = self.client.post(reverse('bookings:booking_approve', kwargs={'pk': booking.pk}), {
                'action': 'approve'
            })
            self.assertEqual(response.status_code, 302)
        
        # 3. 验证所有预约都已确认
        for booking in bookings:
            booking.refresh_from_db()
            self.assertEqual(booking.status, 'confirmed')
    
    def test_search_and_booking_workflow(self):
        """测试搜索和预约工作流程"""
        # 1. 用户搜索特定类型的自习室
        self.login_student()
        
        # 搜索讨论室
        response = self.client.get(reverse('rooms:room_list'), {'search': '讨论'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room2.name)
        self.assertNotContains(response, self.room1.name)
        
        # 2. 查看搜索到的自习室详情
        response = self.client.get(reverse('rooms:room_detail', kwargs={'pk': self.room2.pk}))
        self.assertEqual(response.status_code, 200)
        
        # 3. 预约该自习室
        booking_date = timezone.now().date() + timedelta(days=1)
        response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': self.room2.pk}), {
            'time_slot': self.slot_afternoon.pk,
            'date': booking_date.strftime('%Y-%m-%d'),
            'purpose': '小组讨论',
            'participants': 4
        })
        self.assertEqual(response.status_code, 302)
        
        # 4. 验证预约成功
        booking = self.student_user.booking_set.first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.room, self.room2)
        self.assertEqual(booking.purpose, '小组讨论')


class PermissionIntegrationTest(BaseTestCase):
    """权限集成测试"""
    
    def test_student_access_permissions(self):
        """测试学生访问权限"""
        self.login_student()
        
        # 学生可以访问的页面
        allowed_urls = [
            reverse('rooms:room_list'),
            reverse('rooms:room_detail', kwargs={'pk': self.room1.pk}),
            reverse('bookings:booking_list'),
            reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}),
            reverse('accounts:profile')
        ]
        
        for url in allowed_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302])  # 200 or redirect to login
        
        # 学生不能访问的页面
        forbidden_urls = [
            reverse('bookings:admin_booking_list'),
        ]
        
        for url in forbidden_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [403, 302])  # 403 or redirect
    
    def test_admin_access_permissions(self):
        """测试管理员访问权限"""
        self.login_admin()
        
        # 管理员可以访问所有页面
        all_urls = [
            reverse('rooms:room_list'),
            reverse('rooms:room_detail', kwargs={'pk': self.room1.pk}),
            reverse('bookings:booking_list'),
            reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}),
            reverse('bookings:admin_booking_list'),
            reverse('accounts:profile')
        ]
        
        for url in all_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


class DataConsistencyTest(BaseTestCase):
    """数据一致性测试"""
    
    def test_booking_history_consistency(self):
        """测试预约历史一致性"""
        booking = self.create_test_booking(user=self.student_user, status='pending')
        
        # 检查创建时的历史记录数量
        from bookings.models import BookingHistory
        initial_count = BookingHistory.objects.filter(booking=booking).count()
        
        # 管理员审批
        self.login_admin()
        self.client.post(reverse('bookings:booking_approve', kwargs={'pk': booking.pk}), {
            'action': 'approve'
        })
        
        # 检查历史记录是否增加
        final_count = BookingHistory.objects.filter(booking=booking).count()
        self.assertGreater(final_count, initial_count)
    
    def test_booking_status_transitions(self):
        """测试预约状态转换"""
        booking = self.create_test_booking(user=self.student_user, status='pending')
        
        # pending -> confirmed
        self.login_admin()
        self.client.post(reverse('bookings:booking_approve', kwargs={'pk': booking.pk}), {
            'action': 'approve'
        })
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        
        # confirmed -> cancelled (通过用户取消)
        self.login_student()
        response = self.client.post(reverse('bookings:booking_cancel', kwargs={'pk': booking.pk}))
        
        # 确认的预约不应该被普通用户取消
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')  # 状态不应该改变
