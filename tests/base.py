"""
测试工具类和基础设置
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, date, time, timedelta
import json

from accounts.models import User
from rooms.models import StudyRoom, TimeSlot
from bookings.models import Booking, BookingHistory

User = get_user_model()


class BaseTestCase(TestCase):
    """基础测试类，包含通用的测试数据创建方法"""
    
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.create_test_users()
        self.create_test_rooms()
        self.create_test_time_slots()
    
    def create_test_users(self):
        """创建测试用户"""
        # 普通学生用户
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@test.com',
            password='testpass123',
            user_type='student',
            first_name='张',
            last_name='三',
            phone='13800138001',
            student_id='2021001'
        )
        
        # 教师用户
        self.teacher_user = User.objects.create_user(
            username='teacher1',
            email='teacher1@test.com',
            password='testpass123',
            user_type='teacher',
            first_name='李',
            last_name='老师',
            phone='13800138002',
            student_id='T2021001'
        )
        
        # 管理员用户
        self.admin_user = User.objects.create_user(
            username='admin1',
            email='admin1@test.com',
            password='testpass123',
            user_type='admin',
            first_name='王',
            last_name='管理员',
            phone='13800138003',
            is_staff=True
        )
        
        # 超级管理员
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='superuser@test.com',
            password='testpass123',
            first_name='超级',
            last_name='管理员'
        )
    
    def create_test_rooms(self):
        """创建测试自习室"""
        self.room1 = StudyRoom.objects.create(
            name='101自习室',
            description='安静的学习环境，适合个人学习',
            capacity=30,
            location='教学楼A-101',
            equipment='投影仪、空调、WiFi',
            is_active=True
        )
        
        self.room2 = StudyRoom.objects.create(
            name='201讨论室',
            description='小组讨论专用，配备白板和会议桌',
            capacity=8,
            location='教学楼A-201',
            equipment='白板、会议桌、音响设备',
            is_active=True
        )
        
        self.room3 = StudyRoom.objects.create(
            name='301机房',
            description='计算机实训室',
            capacity=40,
            location='教学楼B-301',
            equipment='电脑40台、投影仪、空调',
            is_active=False  # 测试非活跃房间
        )
    
    def create_test_time_slots(self):
        """创建测试时间段"""
        self.slot_morning = TimeSlot.objects.create(
            name='上午',
            start_time=time(8, 0),
            end_time=time(12, 0),
            is_active=True
        )
        
        self.slot_afternoon = TimeSlot.objects.create(
            name='下午',
            start_time=time(14, 0),
            end_time=time(18, 0),
            is_active=True
        )
        
        self.slot_evening = TimeSlot.objects.create(
                        name='晚上',
            start_time=time(19, 0),
            end_time=time(22, 0),
            is_active=True
        )
        
        self.slot_inactive = TimeSlot.objects.create(
            name='深夜',
            start_time=time(22, 0),
            end_time=time(23, 59),
            is_active=False  # 测试非活跃时间段
        )
    
    def create_test_booking(self, user=None, room=None, time_slot=None, 
                          booking_date=None, status='pending'):
        """创建测试预约"""
        user = user or self.student_user
        room = room or self.room1
        time_slot = time_slot or self.slot_morning
        booking_date = booking_date or timezone.now().date() + timedelta(days=1)
        
        return Booking.objects.create(
            user=user,
            room=room,
            time_slot=time_slot,
            date=booking_date,
            purpose='测试预约',
            participants=1,
            status=status
        )
    
    def login_user(self, user):
        """登录指定用户"""
        self.client.login(username=user.username, password='testpass123')
    
    def login_student(self):
        """登录学生用户"""
        self.login_user(self.student_user)
    
    def login_teacher(self):
        """登录教师用户"""
        self.login_user(self.teacher_user)
    
    def login_admin(self):
        """登录管理员用户"""
        self.login_user(self.admin_user)
    
    def login_superuser(self):
        """登录超级管理员"""
        self.login_user(self.superuser)


class APITestMixin:
    """API测试混入类"""
    
    def api_get(self, url, data=None):
        """发送GET请求"""
        return self.client.get(url, data=data, content_type='application/json')
    
    def api_post(self, url, data=None):
        """发送POST请求"""
        return self.client.post(
            url, 
            data=json.dumps(data) if data else None,
            content_type='application/json'
        )
    
    def api_put(self, url, data=None):
        """发送PUT请求"""
        return self.client.put(
            url,
            data=json.dumps(data) if data else None,
            content_type='application/json'
        )
    
    def api_delete(self, url):
        """发送DELETE请求"""
        return self.client.delete(url, content_type='application/json')
    
    def assert_api_success(self, response, status_code=200):
        """断言API响应成功"""
        self.assertEqual(response.status_code, status_code)
        if response.content:
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                pass
        return None
    
    def assert_api_error(self, response, status_code=400):
        """断言API响应错误"""
        self.assertEqual(response.status_code, status_code)


class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def create_user(username, user_type='student', **kwargs):
        """创建用户"""
        defaults = {
            'email': f'{username}@test.com',
            'password': 'testpass123',
            'user_type': user_type,
            'first_name': '测试',
            'last_name': '用户'
        }
        defaults.update(kwargs)
        
        password = defaults.pop('password')
        user = User.objects.create_user(username=username, **defaults)
        user.set_password(password)
        user.save()
        return user
    
    @staticmethod
    def create_room(name, **kwargs):
        """创建自习室"""
        defaults = {
            'description': f'{name}的描述',
            'capacity': 30,
            'location': f'测试位置-{name}',
            'equipment': '基础设备',
            'is_active': True
        }
        defaults.update(kwargs)
        
        return StudyRoom.objects.create(name=name, **defaults)
    
    @staticmethod
    def create_time_slot(name, start_hour, end_hour, **kwargs):
        """创建时间段"""
        defaults = {
            'start_time': time(start_hour, 0),
            'end_time': time(end_hour, 0),
            'is_active': True
        }
        defaults.update(kwargs)
        
        return TimeSlot.objects.create(name=name, **defaults)
    
    @staticmethod
    def create_booking(user, room, time_slot, **kwargs):
        """创建预约"""
        defaults = {
            'date': timezone.now().date() + timedelta(days=1),
            'purpose': '测试预约',
            'participants': 1,
            'status': 'pending'
        }
        defaults.update(kwargs)
        
        return Booking.objects.create(
            user=user,
            room=room,
            time_slot=time_slot,
            **defaults
        )
