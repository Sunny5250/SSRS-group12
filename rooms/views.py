from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import StudyRoom, TimeSlot


class RoomListView(LoginRequiredMixin, ListView):
    """自习室列表视图"""
    model = StudyRoom
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = StudyRoom.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class RoomDetailView(LoginRequiredMixin, DetailView):
    """自习室详情视图"""
    model = StudyRoom
    template_name = 'rooms/room_detail.html'
    context_object_name = 'room'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_slots'] = TimeSlot.objects.filter(is_active=True).order_by('start_time')
        return context
