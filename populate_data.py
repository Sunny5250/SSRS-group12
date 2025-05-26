import os
import django
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_room_system.settings')
django.setup()

from rooms.models import StudyRoom, TimeSlot
from accounts.models import User
from bookings.models import Booking
from django.utils import timezone
from datetime import time, date, timedelta

def create_sample_data():
    """创建示例数据"""
    print("🚀 开始创建示例数据...")
    
    # 创建时间段
    time_slots = [
        ('上午第一节', time(8, 0), time(9, 30)),
        ('上午第二节', time(9, 50), time(11, 20)),
        ('上午第三节', time(11, 40), time(12, 10)),
        ('下午第一节', time(14, 0), time(15, 30)),
        ('下午第二节', time(15, 50), time(17, 20)),
        ('晚上第一节', time(19, 0), time(20, 30)),
        ('晚上第二节', time(20, 50), time(22, 20)),
    ]
    
    print("📅 创建时间段...")
    for name, start, end in time_slots:
        slot, created = TimeSlot.objects.get_or_create(
            name=name,
            defaults={'start_time': start, 'end_time': end}
        )
        if created:
            print(f"  ✅ 创建时间段: {name}")
    
    # 创建自习室
    rooms_data = [
        {
            'name': '图书馆101自习室',
            'description': '安静的学习环境，配备空调和免费WiFi，适合深度学习和研究。',
            'capacity': 30,
            'location': '图书馆一楼101室',
            'equipment': '空调、WiFi、投影仪、白板、充电插座'
        },
        {
            'name': '图书馆201自习室',
            'description': '宽敞明亮的学习空间，采光良好，环境优雅。',
            'capacity': 25,
            'location': '图书馆二楼201室',
            'equipment': '空调、WiFi、台灯、书架'
        },
        {
            'name': '实验楼A305',
            'description': '配备现代化设施的多功能学习室，支持小组讨论。',
            'capacity': 20,
            'location': '实验楼A座305室',
            'equipment': '空调、WiFi、投影仪、音响、移动白板'
        },
        {
            'name': '教学楼B502',
            'description': '传统教室改造的自习室，座位舒适，视野开阔。',
            'capacity': 35,
            'location': '教学楼B座502室',
            'equipment': '空调、WiFi、黑板、充电插座'
        },
        {
            'name': '研究生楼C201',
            'description': '专为研究生设计的高端学习空间，配备个人学习隔间。',
            'capacity': 15,
            'location': '研究生楼C座201室',
            'equipment': '空调、WiFi、个人隔间、台灯、储物柜'
        },
        {
            'name': '综合楼D401',
            'description': '24小时开放的自习室，适合夜猫子学习。',
            'capacity': 40,
            'location': '综合楼D座401室',
            'equipment': '空调、WiFi、夜间照明、安全监控'
        }
    ]
    
    print("🏢 创建自习室...")
    for room_data in rooms_data:
        room, created = StudyRoom.objects.get_or_create(
            name=room_data['name'],
            defaults=room_data
        )
        if created:
            print(f"  ✅ 创建自习室: {room_data['name']}")
    
    # 创建测试用户
    users_data = [
        {
            'username': 'student1',
            'email': 'student1@example.com',
            'user_type': 'student',
            'student_id': '2023001',
            'phone': '13800138001'
        },
        {
            'username': 'student2', 
            'email': 'student2@example.com',
            'user_type': 'student',
            'student_id': '2023002',
            'phone': '13800138002'
        },
        {
            'username': 'teacher1',
            'email': 'teacher1@example.com', 
            'user_type': 'teacher',
            'student_id': 'T001',
            'phone': '13800138003'
        }
    ]
    
    print("👥 创建测试用户...")
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                **user_data,
                'first_name': user_data['username'],
                'last_name': '测试'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"  ✅ 创建用户: {user_data['username']} (密码: testpass123)")
    
    print("✨ 示例数据创建完成!")
    print("\n📊 数据统计:")
    print(f"  时间段: {TimeSlot.objects.count()} 个")
    print(f"  自习室: {StudyRoom.objects.count()} 个") 
    print(f"  用户: {User.objects.count()} 个")
    print(f"  预约: {Booking.objects.count()} 个")
    
    print("\n🔑 管理员账号:")
    admin_users = User.objects.filter(is_superuser=True)
    for admin in admin_users:
        print(f"  用户名: {admin.username}")
    
    print("\n🧪 测试账号:")
    for user_data in users_data:
        print(f"  用户名: {user_data['username']}, 密码: testpass123, 类型: {user_data['user_type']}")

if __name__ == "__main__":
    create_sample_data()
