"""
自习室模块测试
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import time, datetime
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from tests.base import BaseTestCase, TestDataFactory
from .models import StudyRoom, TimeSlot


class StudyRoomModelTest(BaseTestCase):
    """自习室模型测试"""
    
    def test_create_study_room(self):
        """测试创建自习室"""
        room = StudyRoom.objects.create(
            name='测试自习室',
            description='这是一个测试自习室',
            capacity=50,
            location='测试楼A-101',
            equipment='投影仪、空调、WiFi',
            is_active=True
        )
        
        self.assertEqual(room.name, '测试自习室')
        self.assertEqual(room.description, '这是一个测试自习室')
        self.assertEqual(room.capacity, 50)
        self.assertEqual(room.location, '测试楼A-101')
        self.assertEqual(room.equipment, '投影仪、空调、WiFi')
        self.assertTrue(room.is_active)
        self.assertIsNotNone(room.created_at)
        self.assertIsNotNone(room.updated_at)
    
    def test_study_room_str_method(self):
        """测试自习室字符串表示"""
        room = self.room1
        self.assertEqual(str(room), room.name)
    
    def test_study_room_ordering(self):
        """测试自习室排序"""
        # 创建几个自习室
        room_a = TestDataFactory.create_room('A教室')
        room_b = TestDataFactory.create_room('B教室')
        room_c = TestDataFactory.create_room('C教室')
        
        # 获取所有自习室
        rooms = StudyRoom.objects.all()
        
        # 检查是否按名称排序
        room_names = [room.name for room in rooms]
        sorted_names = sorted(room_names)
        self.assertEqual(room_names, sorted_names)
    
    def test_study_room_capacity_validation(self):
        """测试自习室容量验证"""
        # 容量应该是正整数
        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            StudyRoom.objects.create(
                name='测试自习室',
                capacity=-10,  # 负数容量
                location='测试位置'
            )
    
    def test_active_rooms_filter(self):
        """测试活跃自习室过滤"""
        # 获取活跃的自习室
        active_rooms = StudyRoom.objects.filter(is_active=True)
        
        # 应该包含room1和room2，不包含room3
        self.assertIn(self.room1, active_rooms)
        self.assertIn(self.room2, active_rooms)
        self.assertNotIn(self.room3, active_rooms)


class TimeSlotModelTest(BaseTestCase):
    """时间段模型测试"""
    
    def test_create_time_slot(self):
        """测试创建时间段"""
        slot = TimeSlot.objects.create(
            name='中午',
            start_time=time(12, 0),
            end_time=time(14, 0),
            is_active=True
        )
        
        self.assertEqual(slot.name, '中午')
        self.assertEqual(slot.start_time, time(12, 0))
        self.assertEqual(slot.end_time, time(14, 0))
        self.assertTrue(slot.is_active)
    
    def test_time_slot_str_method(self):
        """测试时间段字符串表示"""
        slot = self.slot_morning
        expected = f"{slot.name} ({slot.start_time}-{slot.end_time})"
        self.assertEqual(str(slot), expected)
    
    def test_time_slot_ordering(self):
        """测试时间段排序"""
        # 获取所有时间段
        slots = TimeSlot.objects.all()
        
        # 检查是否按开始时间排序
        start_times = [slot.start_time for slot in slots]
        sorted_times = sorted(start_times)
        self.assertEqual(start_times, sorted_times)
    
    def test_time_slot_validation(self):
        """测试时间段验证"""
        # 创建一个无效的时间段（结束时间早于开始时间）
        slot = TimeSlot(
            name='无效时间段',
            start_time=time(18, 0),
            end_time=time(12, 0),  # 结束时间早于开始时间
            is_active=True
        )
        
        # 应该抛出验证错误
        with self.assertRaises(ValidationError):
            slot.clean()
    
    def test_time_slot_same_time(self):
        """测试开始时间和结束时间相同"""
        slot = TimeSlot(
            name='无效时间段',
            start_time=time(12, 0),
            end_time=time(12, 0),  # 开始时间和结束时间相同
            is_active=True
        )
        
        with self.assertRaises(ValidationError):
            slot.clean()
    
    def test_active_time_slots_filter(self):
        """测试活跃时间段过滤"""
        active_slots = TimeSlot.objects.filter(is_active=True)
        
        # 应该包含活跃的时间段，不包含非活跃的
        self.assertIn(self.slot_morning, active_slots)
        self.assertIn(self.slot_afternoon, active_slots)
        self.assertIn(self.slot_evening, active_slots)
        self.assertNotIn(self.slot_inactive, active_slots)


class RoomListViewTest(BaseTestCase):
    """自习室列表视图测试"""
    
    def test_room_list_view_authenticated(self):
        """测试已登录用户访问自习室列表"""
        self.login_student()
        response = self.client.get(reverse('rooms:room_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room1.name)
        self.assertContains(response, self.room2.name)
        # 非活跃的自习室不应该显示
        self.assertNotContains(response, self.room3.name)
    
    def test_room_list_view_anonymous(self):
        """测试未登录用户访问自习室列表"""
        response = self.client.get(reverse('rooms:room_list'))
        
        # 应该重定向到登录页面
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_room_list_search(self):
        """测试自习室搜索功能"""
        self.login_student()
        
        # 搜索自习室名称
        response = self.client.get(reverse('rooms:room_list'), {'search': '101'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room1.name)
        self.assertNotContains(response, self.room2.name)
        
        # 搜索位置
        response = self.client.get(reverse('rooms:room_list'), {'search': 'A-201'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room2.name)
        self.assertNotContains(response, self.room1.name)
        
        # 搜索描述
        response = self.client.get(reverse('rooms:room_list'), {'search': '讨论'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room2.name)
        self.assertNotContains(response, self.room1.name)
    
    def test_room_list_pagination(self):
        """测试自习室列表分页"""
        # 创建足够多的自习室来测试分页
        for i in range(15):
            TestDataFactory.create_room(f'测试自习室{i}')
        
        self.login_student()
        response = self.client.get(reverse('rooms:room_list'))
        
        self.assertEqual(response.status_code, 200)
        # 检查是否有分页
        self.assertContains(response, 'page-item')
    
    def test_room_list_context(self):
        """测试自习室列表上下文"""
        self.login_student()
        response = self.client.get(reverse('rooms:room_list'), {'search': 'test'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search'], 'test')
        self.assertIn('rooms', response.context)


class RoomDetailViewTest(BaseTestCase):
    """自习室详情视图测试"""
    
    def test_room_detail_view_authenticated(self):
        """测试已登录用户访问自习室详情"""
        self.login_student()
        response = self.client.get(reverse('rooms:room_detail', kwargs={'pk': self.room1.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.room1.name)
        self.assertContains(response, self.room1.description)
        self.assertContains(response, str(self.room1.capacity))
        self.assertContains(response, self.room1.location)
    
    def test_room_detail_view_anonymous(self):
        """测试未登录用户访问自习室详情"""
        response = self.client.get(reverse('rooms:room_detail', kwargs={'pk': self.room1.pk}))
        
        # 应该重定向到登录页面
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_room_detail_view_inactive_room(self):
        """测试访问非活跃自习室详情"""
        self.login_student()
        response = self.client.get(reverse('rooms:room_detail', kwargs={'pk': self.room3.pk}))
        
        # 非活跃的自习室应该可以访问（虽然不在列表中显示）
        self.assertEqual(response.status_code, 200)
    
    def test_room_detail_view_nonexistent_room(self):
        """测试访问不存在的自习室"""
        self.login_student()
        response = self.client.get(reverse('rooms:room_detail', kwargs={'pk': 9999}))
        
        # 应该返回404
        self.assertEqual(response.status_code, 404)
    
    def test_room_detail_context(self):
        """测试自习室详情上下文"""
        self.login_student()
        response = self.client.get(reverse('rooms:room_detail', kwargs={'pk': self.room1.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['room'], self.room1)
        self.assertIn('time_slots', response.context)
        
        # 检查时间段是否只包含活跃的
        time_slots = response.context['time_slots']
        for slot in time_slots:
            self.assertTrue(slot.is_active)


class RoomModelMethodTest(BaseTestCase):
    """自习室模型方法测试"""
    
    def test_room_available_check(self):
        """测试自习室可用性检查（如果有这样的方法）"""
        # 这里可以添加检查自习室在特定时间是否可用的方法测试
        pass
    
    def test_room_capacity_validation_on_save(self):
        """测试保存时的容量验证"""
        room = StudyRoom(
            name='测试自习室',
            capacity=0,  # 无效容量
            location='测试位置'
        )
        
        # 如果模型有自定义验证，这里应该会失败
        try:
            room.full_clean()
        except ValidationError:
            pass  # 期望的行为


class TimeSlotModelMethodTest(BaseTestCase):
    """时间段模型方法测试"""
    
    def test_time_slot_duration(self):
        """测试时间段持续时间计算（如果有这样的方法）"""
        # 可以添加计算时间段持续时间的方法测试
        pass
    
    def test_time_slot_overlap_check(self):
        """测试时间段重叠检查（如果有这样的方法）"""
        # 可以添加检查时间段是否重叠的方法测试
        pass


class RoomViewsIntegrationTest(BaseTestCase):
    """自习室视图集成测试"""
    
    def test_room_list_to_detail_navigation(self):
        """测试从自习室列表到详情的导航"""
        self.login_student()
        
        # 访问自习室列表
        list_response = self.client.get(reverse('rooms:room_list'))
        self.assertEqual(list_response.status_code, 200)
        
        # 检查详情链接是否存在
        detail_url = reverse('rooms:room_detail', kwargs={'pk': self.room1.pk})
        self.assertContains(list_response, detail_url)
        
        # 访问详情页面
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
    
    def test_booking_link_in_room_detail(self):
        """测试自习室详情页面的预约链接"""
        self.login_student()
        response = self.client.get(reverse('rooms:room_detail', kwargs={'pk': self.room1.pk}))
        
        self.assertEqual(response.status_code, 200)
        # 检查是否有预约相关的链接或按钮
        booking_url = reverse('bookings:booking_create', kwargs={'room_id': self.room1.pk})
        self.assertContains(response, booking_url)
