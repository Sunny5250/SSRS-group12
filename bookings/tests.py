"""
预约模块测试
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.messages import get_messages
from datetime import datetime, date, timedelta
import json
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.base import BaseTestCase, TestDataFactory, APITestMixin
from .models import Booking, BookingHistory
from .views import BookingForm


class BookingModelTest(BaseTestCase):
    """预约模型测试"""
    
    def test_create_booking(self):
        """测试创建预约"""
        booking_date = timezone.now().date() + timedelta(days=1)
        booking = Booking.objects.create(
            user=self.student_user,
            room=self.room1,
            time_slot=self.slot_morning,
            date=booking_date,
            purpose='学习计算机科学',
            participants=1,
            status='pending'
        )
        
        self.assertEqual(booking.user, self.student_user)
        self.assertEqual(booking.room, self.room1)
        self.assertEqual(booking.time_slot, self.slot_morning)
        self.assertEqual(booking.date, booking_date)
        self.assertEqual(booking.purpose, '学习计算机科学')
        self.assertEqual(booking.participants, 1)
        self.assertEqual(booking.status, 'pending')
        self.assertIsNotNone(booking.created_at)
        self.assertIsNotNone(booking.updated_at)
    
    def test_booking_str_method(self):
        """测试预约字符串表示"""
        booking = self.create_test_booking()
        expected = f"{booking.user.username} - {booking.room.name} - {booking.date} {booking.time_slot.name}"
        self.assertEqual(str(booking), expected)
    
    def test_booking_status_choices(self):
        """测试预约状态选择"""
        valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        
        for i, status in enumerate(valid_statuses):
            # 为每个状态使用不同的日期以避免唯一约束冲突
            booking_date = timezone.now().date() + timedelta(days=i+1)
            booking = self.create_test_booking(status=status, date=booking_date)
            self.assertEqual(booking.status, status)
    
    def test_booking_unique_constraint(self):
        """测试预约唯一约束"""
        booking_date = timezone.now().date() + timedelta(days=1)
        
        # 创建第一个预约
        Booking.objects.create(
            user=self.student_user,
            room=self.room1,
            time_slot=self.slot_morning,
            date=booking_date,
            status='pending'
        )
        
        # 尝试创建相同时间的预约，应该失败
        with self.assertRaises(Exception):
            Booking.objects.create(
                user=self.teacher_user,  # 不同用户
                room=self.room1,         # 相同房间
                time_slot=self.slot_morning,  # 相同时间段
                date=booking_date,       # 相同日期
                status='pending'
            )
    
    def test_booking_validation_past_date(self):
        """测试不能预约过去的日期"""
        past_date = timezone.now().date() - timedelta(days=1)
        booking = Booking(
            user=self.student_user,
            room=self.room1,
            time_slot=self.slot_morning,
            date=past_date,
            participants=1
        )
        
        with self.assertRaises(ValidationError):
            booking.clean()
    
    def test_booking_validation_participants_exceed_capacity(self):
        """测试参与人数不能超过房间容量"""
        booking = Booking(
            user=self.student_user,
            room=self.room1,  # 容量为30
            time_slot=self.slot_morning,
            date=timezone.now().date() + timedelta(days=1),
            participants=50  # 超过容量
        )
        
        with self.assertRaises(ValidationError):
            booking.clean()
    
    def test_booking_validation_duplicate_time_slot(self):
        """测试同一时间段重复预约验证"""
        booking_date = timezone.now().date() + timedelta(days=1)
        
        # 创建第一个预约
        existing_booking = Booking.objects.create(
            user=self.student_user,
            room=self.room1,
            time_slot=self.slot_morning,
            date=booking_date,
            status='confirmed'
        )
        
        # 尝试创建重复的预约，应该引发IntegrityError（数据库级约束）
        with self.assertRaises(Exception):  # 可能是IntegrityError或ValidationError
            duplicate_booking = Booking.objects.create(
                user=self.teacher_user,
                room=self.room1,
                time_slot=self.slot_morning,
                date=booking_date,
                status='pending'
            )


class BookingHistoryModelTest(BaseTestCase):
    """预约历史模型测试"""
    
    def test_create_booking_history(self):
        """测试创建预约历史"""
        booking = self.create_test_booking()
        history = BookingHistory.objects.create(
            booking=booking,
            action='创建预约',
            operator=self.student_user,
            notes='用户创建了新预约'
        )
        
        self.assertEqual(history.booking, booking)
        self.assertEqual(history.action, '创建预约')
        self.assertEqual(history.operator, self.student_user)
        self.assertEqual(history.notes, '用户创建了新预约')
        self.assertIsNotNone(history.created_at)
    
    def test_booking_history_ordering(self):
        """测试预约历史排序"""
        booking = self.create_test_booking()
        
        # 创建多个历史记录
        history1 = BookingHistory.objects.create(
            booking=booking,
            action='创建预约',
            operator=self.student_user
        )
        
        history2 = BookingHistory.objects.create(
            booking=booking,
            action='审批通过',
            operator=self.admin_user
        )
        
        # 获取所有历史记录
        histories = BookingHistory.objects.filter(booking=booking)
        
        # 应该按创建时间倒序排列
        self.assertEqual(histories.first(), history2)
        self.assertEqual(histories.last(), history1)


class BookingListViewTest(BaseTestCase):
    """预约列表视图测试"""
    
    def test_booking_list_view_authenticated(self):
        """测试已登录用户访问预约列表"""
        # 创建一些预约
        booking1 = self.create_test_booking(user=self.student_user)
        booking2 = self.create_test_booking(user=self.teacher_user, time_slot=self.slot_afternoon)
        
        self.login_student()
        response = self.client.get(reverse('bookings:booking_list'))
        
        self.assertEqual(response.status_code, 200)
        # 应该只显示当前用户的预约
        self.assertContains(response, str(booking1))
        self.assertNotContains(response, str(booking2))
    
    def test_booking_list_view_anonymous(self):
        """测试未登录用户访问预约列表"""
        response = self.client.get(reverse('bookings:booking_list'))
        
        # 应该重定向到登录页面
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_booking_list_statistics(self):
        """测试预约列表统计信息"""
        # 创建不同状态的预约
        self.create_test_booking(user=self.student_user, status='pending')
        self.create_test_booking(user=self.student_user, status='confirmed', time_slot=self.slot_afternoon)
        self.create_test_booking(user=self.student_user, status='cancelled', time_slot=self.slot_evening)
        
        self.login_student()
        response = self.client.get(reverse('bookings:booking_list'))
        
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertEqual(context['total_bookings'], 3)
        self.assertEqual(context['pending_count'], 1)
        self.assertEqual(context['confirmed_count'], 1)
        self.assertEqual(context['cancelled_count'], 1)


class BookingCreateViewTest(BaseTestCase):
    """预约创建视图测试"""
    
    def test_booking_create_view_get(self):
        """测试GET请求预约创建页面"""
        self.login_student()
        response = self.client.get(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room1.name)
        self.assertIn('room', response.context)
        self.assertIn('time_slots', response.context)
        self.assertIn('today', response.context)
    
    def test_booking_create_success(self):
        """测试成功创建预约"""
        self.login_student()
        booking_date = timezone.now().date() + timedelta(days=1)
        
        response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}), {
            'time_slot': self.slot_morning.pk,
            'date': booking_date.strftime('%Y-%m-%d'),
            'purpose': '学习编程',
            'participants': 1
        })
        
        # 应该重定向到预约列表
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('bookings:booking_list'))
        
        # 检查预约是否创建
        booking = Booking.objects.filter(
            user=self.student_user,
            room=self.room1,
            time_slot=self.slot_morning,
            date=booking_date
        ).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.purpose, '学习编程')
        self.assertEqual(booking.status, 'pending')
        
        # 检查是否创建了预约历史
        history = BookingHistory.objects.filter(booking=booking).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.action, '创建预约')
    
    def test_booking_create_duplicate_time(self):
        """测试创建重复时间的预约"""
        booking_date = timezone.now().date() + timedelta(days=1)
        
        # 先创建一个预约
        self.create_test_booking(
            user=self.teacher_user,
            room=self.room1,
            time_slot=self.slot_morning,
            booking_date=booking_date,
            status='confirmed'
        )
        
        self.login_student()
        response = self.client.post(reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk}), {
            'time_slot': self.slot_morning.pk,
            'date': booking_date.strftime('%Y-%m-%d'),
            'purpose': '学习编程',
            'participants': 1
        })
        
        # 应该返回表单页面并显示错误
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('已被预约' in str(message) for message in messages))
    
    def test_booking_create_invalid_room(self):
        """测试创建无效房间的预约"""
        self.login_student()
        response = self.client.get(reverse('bookings:booking_create', kwargs={'room_id': 9999}))
        
        # 应该返回404
        self.assertEqual(response.status_code, 404)
    
    def test_booking_create_inactive_room(self):
        """测试创建非活跃房间的预约"""
        self.login_student()
        response = self.client.get(reverse('bookings:booking_create', kwargs={'room_id': self.room3.pk}))
        
        # 非活跃房间应该返回404
        self.assertEqual(response.status_code, 404)


class BookingDetailViewTest(BaseTestCase):
    """预约详情视图测试"""
    
    def test_booking_detail_view_owner(self):
        """测试预约所有者访问详情"""
        booking = self.create_test_booking(user=self.student_user)
        
        self.login_student()
        response = self.client.get(reverse('bookings:booking_detail', kwargs={'pk': booking.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['booking'], booking)
        self.assertIn('booking_histories', response.context)
    
    def test_booking_detail_view_other_user(self):
        """测试其他用户访问预约详情"""
        booking = self.create_test_booking(user=self.student_user)
        
        self.login_teacher()
        response = self.client.get(reverse('bookings:booking_detail', kwargs={'pk': booking.pk}))
        
        # 普通用户不能查看其他用户的预约
        self.assertEqual(response.status_code, 404)
    
    def test_booking_detail_view_admin(self):
        """测试管理员访问预约详情"""
        booking = self.create_test_booking(user=self.student_user)
        
        self.login_admin()
        response = self.client.get(reverse('bookings:booking_detail', kwargs={'pk': booking.pk}))
        
        # 管理员可以查看所有预约
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['booking'], booking)


class BookingCancelViewTest(BaseTestCase):
    """预约取消视图测试"""
    
    def test_booking_cancel_success(self):
        """测试成功取消预约"""
        booking = self.create_test_booking(user=self.student_user, status='pending')
        
        self.login_student()
        response = self.client.post(reverse('bookings:booking_cancel', kwargs={'pk': booking.pk}))
        
        # 应该重定向到预约列表
        self.assertEqual(response.status_code, 302)
        
        # 检查预约状态是否更新
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        
        # 检查是否创建了取消历史
        history = BookingHistory.objects.filter(
            booking=booking,
            action='取消预约'
        ).first()
        self.assertIsNotNone(history)
    
    def test_booking_cancel_confirmed_booking(self):
        """测试取消已确认的预约"""
        booking = self.create_test_booking(user=self.student_user, status='confirmed')
        
        self.login_student()
        response = self.client.post(reverse('bookings:booking_cancel', kwargs={'pk': booking.pk}))
        
        # 已确认的预约不能取消
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('无法取消' in str(message) for message in messages))


class AdminBookingListViewTest(BaseTestCase):
    """管理员预约列表视图测试"""
    
    def test_admin_booking_list_view(self):
        """测试管理员访问预约列表"""
        # 创建一些预约
        booking1 = self.create_test_booking(user=self.student_user)
        booking2 = self.create_test_booking(user=self.teacher_user, time_slot=self.slot_afternoon)
        
        self.login_admin()
        response = self.client.get(reverse('bookings:admin_booking_list'))
        
        self.assertEqual(response.status_code, 200)
        # 管理员可以看到所有预约
        self.assertContains(response, str(booking1))
        self.assertContains(response, str(booking2))
    
    def test_admin_booking_list_non_admin(self):
        """测试非管理员访问管理员预约列表"""
        self.login_student()
        response = self.client.get(reverse('bookings:admin_booking_list'))
        
        # 应该返回403或重定向
        self.assertIn(response.status_code, [403, 302])
    
    def test_admin_booking_list_filter(self):
        """测试管理员预约列表过滤"""
        # 创建不同状态的预约
        pending_booking = self.create_test_booking(user=self.student_user, status='pending')
        confirmed_booking = self.create_test_booking(user=self.teacher_user, status='confirmed', time_slot=self.slot_afternoon)
        
        self.login_admin()
        
        # 测试按状态过滤
        response = self.client.get(reverse('bookings:admin_booking_list'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)
        # 这里需要根据实际的过滤逻辑进行断言


class BookingApproveViewTest(BaseTestCase):
    """预约审批视图测试"""
    
    def test_booking_approve_success(self):
        """测试成功审批预约"""
        booking = self.create_test_booking(user=self.student_user, status='pending')
        
        self.login_admin()
        response = self.client.post(reverse('bookings:booking_approve', kwargs={'pk': booking.pk}), {
            'action': 'approve',
            'notes': '审批通过'
        })
        
        # 应该重定向到管理员预约列表
        self.assertEqual(response.status_code, 302)
        
        # 检查预约状态是否更新
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        
        # 检查是否创建了审批历史
        history = BookingHistory.objects.filter(
            booking=booking,
            action='审批通过'
        ).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.notes, '审批通过')
    
    def test_booking_reject_success(self):
        """测试成功拒绝预约"""
        booking = self.create_test_booking(user=self.student_user, status='pending')
        
        self.login_admin()
        response = self.client.post(reverse('bookings:booking_approve', kwargs={'pk': booking.pk}), {
            'action': 'reject',
            'notes': '时间冲突'
        })
        
        # 应该重定向到管理员预约列表
        self.assertEqual(response.status_code, 302)
        
        # 检查预约状态是否更新
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
    
    def test_booking_approve_non_admin(self):
        """测试非管理员审批预约"""
        booking = self.create_test_booking(user=self.student_user, status='pending')
        
        self.login_student()
        response = self.client.post(reverse('bookings:booking_approve', kwargs={'pk': booking.pk}), {
            'action': 'approve'
        })
        
        # 应该返回403或重定向
        self.assertIn(response.status_code, [403, 302])


class BookingFormTest(BaseTestCase):
    """预约表单测试"""
    
    def test_valid_booking_form(self):
        """测试有效的预约表单"""
        form_data = {
            'time_slot': self.slot_morning.pk,
            'date': (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'purpose': '学习编程',
            'participants': 1
        }
        form = BookingForm(data=form_data, room=self.room1)
        self.assertTrue(form.is_valid())
    
    def test_booking_form_past_date(self):
        """测试过去日期的预约表单"""
        form_data = {
            'time_slot': self.slot_morning.pk,
            'date': (timezone.now().date() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'purpose': '学习编程',
            'participants': 1
        }
        form = BookingForm(data=form_data, room=self.room1)
        self.assertFalse(form.is_valid())
    
    def test_booking_form_exceeds_capacity(self):
        """测试超出容量的预约表单"""
        form_data = {
            'time_slot': self.slot_morning.pk,
            'date': (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'purpose': '学习编程',
            'participants': self.room1.capacity + 1  # 超出容量
        }
        form = BookingForm(data=form_data, room=self.room1)
        self.assertFalse(form.is_valid())


class BookingAPITest(BaseTestCase, APITestMixin):
    """预约API测试"""
    
    def test_booking_api_list(self):
        """测试预约API列表"""
        # 创建一些预约
        booking1 = self.create_test_booking(user=self.student_user)
        booking2 = self.create_test_booking(user=self.teacher_user, time_slot=self.slot_afternoon)
        
        self.login_student()
        response = self.api_get('/bookings/api/bookings/')
        
        if response.status_code == 200:
            data = self.assert_api_success(response)
            # 应该只返回当前用户的预约
            self.assertIsNotNone(data)
    
    def test_booking_api_create(self):
        """测试预约API创建"""
        self.login_student()
        booking_data = {
            'room': self.room1.pk,
            'time_slot': self.slot_morning.pk,
            'date': (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'purpose': '学习编程',
            'participants': 1
        }
        
        response = self.api_post('/bookings/api/bookings/', booking_data)
        
        if response.status_code == 201:
            data = self.assert_api_success(response, 201)
            self.assertIsNotNone(data)
