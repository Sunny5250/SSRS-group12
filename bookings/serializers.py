from rest_framework import serializers
from .models import Booking
from rooms.models import StudyRoom, TimeSlot
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'student_id']


class StudyRoomSerializer(serializers.ModelSerializer):
    """自习室序列化器"""
    class Meta:
        model = StudyRoom
        fields = ['id', 'name', 'description', 'capacity', 'location', 'equipment', 'image']


class TimeSlotSerializer(serializers.ModelSerializer):
    """时间段序列化器"""
    class Meta:
        model = TimeSlot
        fields = ['id', 'name', 'start_time', 'end_time']


class BookingSerializer(serializers.ModelSerializer):
    """预约序列化器"""
    user = UserSerializer(read_only=True)
    room = StudyRoomSerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    
    # 用于创建预约的字段
    room_id = serializers.IntegerField(write_only=True)
    time_slot_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'room', 'time_slot', 'date', 'purpose', 
            'participants', 'status', 'created_at', 'updated_at',
            'room_id', 'time_slot_id'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        room_id = validated_data.pop('room_id')
        time_slot_id = validated_data.pop('time_slot_id')
        
        room = StudyRoom.objects.get(id=room_id)
        time_slot = TimeSlot.objects.get(id=time_slot_id)
        
        validated_data['room'] = room
        validated_data['time_slot'] = time_slot
        
        return super().create(validated_data)
    
    def validate(self, data):
        # 验证房间和时间段是否存在
        if 'room_id' in data:
            try:
                room = StudyRoom.objects.get(id=data['room_id'], is_active=True)
            except StudyRoom.DoesNotExist:
                raise serializers.ValidationError('指定的自习室不存在或已停用')
        
        if 'time_slot_id' in data:
            try:
                time_slot = TimeSlot.objects.get(id=data['time_slot_id'], is_active=True)
            except TimeSlot.DoesNotExist:
                raise serializers.ValidationError('指定的时间段不存在或已停用')
        
        # 验证参与人数
        if 'room_id' in data and 'participants' in data:
            room = StudyRoom.objects.get(id=data['room_id'])
            if data['participants'] > room.capacity:
                raise serializers.ValidationError(f'参与人数不能超过房间容量({room.capacity})')
        
        # 验证时间段冲突
        if all(key in data for key in ['room_id', 'time_slot_id', 'date']):
            existing = Booking.objects.filter(
                room_id=data['room_id'],
                time_slot_id=data['time_slot_id'],
                date=data['date'],
                status__in=['pending', 'confirmed']
            )
            
            # 如果是更新操作，排除当前预约
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError('该时间段已被预约')
        
        return data
