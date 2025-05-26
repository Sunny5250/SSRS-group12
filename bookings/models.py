from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from rooms.models import StudyRoom, TimeSlot


class Booking(models.Model):
    """预约模型"""
    STATUS_CHOICES = [
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('cancelled', '已取消'),
        ('completed', '已完成'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='预约用户'
    )
    room = models.ForeignKey(
        StudyRoom,
        on_delete=models.CASCADE,
        verbose_name='自习室'
    )
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        verbose_name='时间段'
    )
    date = models.DateField(verbose_name='预约日期')
    purpose = models.TextField(blank=True, verbose_name='使用目的')
    participants = models.PositiveIntegerField(default=1, verbose_name='参与人数')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '预约'
        verbose_name_plural = '预约'
        unique_together = ('room', 'time_slot', 'date')
        ordering = ['-created_at']
    def clean(self):
        """验证预约规则"""
        current_date = timezone.now().date()
        # 检查预约日期不能是过去
        if self.date and self.date < current_date:
            raise ValidationError('不能预约过去的日期')
        
        # 检查人数不能超过房间容量
        if self.room_id and self.participants:
            try:
                room = self.room # This line might still cause issues if self.room is not loaded
                if self.participants > room.capacity:
                    raise ValidationError(f'参与人数不能超过房间容量({room.capacity})')
            except StudyRoom.DoesNotExist:
                # This case should ideally be prevented by form validation or a check for self.room before accessing its attributes
                pass 
        
        # 检查同一时间段是否已被预约
        if self.room_id and self.time_slot_id and self.date:
            # It's generally better to query using the related object itself if available,
            # but using _id fields is fine if the object isn't loaded.
            # However, ensure that room and time_slot are actually set on the instance
            # if you are in a context where they should be (e.g. after form validation and cleaning)
            try:
                existing_booking = Booking.objects.filter(
                    room_id=self.room_id,
                    time_slot_id=self.time_slot_id,
                    date=self.date,
                    status__in=['pending', 'confirmed']
                ).exclude(pk=self.pk)
                
                if existing_booking.exists():
                    raise ValidationError('该时间段已被预约')
            except Exception:
                # Avoid catching generic Exception if possible.
                # Consider what specific exceptions might occur here.
                pass 
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        user_name = self.user.username if self.user else "未知用户"
        room_name = self.room.name if self.room else "未知房间"
        time_slot_name = self.time_slot.name if self.time_slot else "未知时间段"
        return f"{user_name} - {room_name} - {self.date} {time_slot_name}"


class BookingHistory(models.Model):
    """预约历史记录"""
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        verbose_name='预约'
    )
    action = models.CharField(max_length=50, verbose_name='操作')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='操作者'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    
    class Meta:
        verbose_name = '预约历史'
        verbose_name_plural = '预约历史'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking} - {self.action}"
