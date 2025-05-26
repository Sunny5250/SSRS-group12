from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from datetime import datetime
from .models import Booking
from rooms.models import StudyRoom, TimeSlot
from .serializers import (
    BookingSerializer, StudyRoomSerializer, TimeSlotSerializer
)


class RoomListAPIView(generics.ListAPIView):
    """自习室列表API"""
    queryset = StudyRoom.objects.filter(is_active=True)
    serializer_class = StudyRoomSerializer
    permission_classes = [IsAuthenticated]


class RoomDetailAPIView(generics.RetrieveAPIView):
    """自习室详情API"""
    queryset = StudyRoom.objects.filter(is_active=True)
    serializer_class = StudyRoomSerializer
    permission_classes = [IsAuthenticated]


class BookingListCreateAPIView(generics.ListCreateAPIView):
    """预约列表和创建API"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """预约详情API"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin' or self.request.user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)


class TimeSlotListAPIView(generics.ListAPIView):
    """时间段列表API"""
    queryset = TimeSlot.objects.filter(is_active=True)
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]


class AvailableSlotsAPIView(generics.GenericAPIView):
    """查询可用时间段API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, room_id, date):
        try:
            room = get_object_or_404(StudyRoom, pk=room_id, is_active=True)
            date_obj = parse_date(date)
            
            if not date_obj:
                return Response(
                    {'error': '日期格式无效'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 获取所有时间段
            all_slots = TimeSlot.objects.filter(is_active=True)
            
            # 获取已预约的时间段
            booked_slots = Booking.objects.filter(
                room=room,
                date=date_obj,
                status__in=['pending', 'confirmed']
            ).values_list('time_slot_id', flat=True)
            
            # 过滤出可用时间段
            available_slots = all_slots.exclude(id__in=booked_slots)
            
            serializer = TimeSlotSerializer(available_slots, many=True)
            return Response({
                'room': room.name,
                'date': date,
                'available_slots': serializer.data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
