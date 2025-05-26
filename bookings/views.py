from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, date
from .models import Booking, BookingHistory
from rooms.models import StudyRoom, TimeSlot
from django import forms


class BookingForm(forms.ModelForm):
    """预约表单"""
    class Meta:
        model = Booking
        fields = ['time_slot', 'date', 'purpose', 'participants']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'min': date.today()}),
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        self.room = kwargs.pop('room', None)
        super().__init__(*args, **kwargs)
        self.fields['time_slot'].queryset = TimeSlot.objects.filter(is_active=True)
        
    def clean_date(self):
        date_value = self.cleaned_data['date']
        today = timezone.now().date()
        if date_value < today:
            raise forms.ValidationError('不能预约过去的日期')
        return date_value
        
    def clean_participants(self):
        participants = self.cleaned_data['participants']
        if self.room and participants > self.room.capacity:
            raise forms.ValidationError(f'参与人数不能超过房间容量({self.room.capacity})')
        return participants


class BookingListView(LoginRequiredMixin, ListView):
    """用户预约列表视图"""
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('room', 'time_slot', 'user').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 计算用户不同状态预约的统计数据
        user_bookings = Booking.objects.filter(user=self.request.user)
        context['total_bookings'] = user_bookings.count()
        context['pending_count'] = user_bookings.filter(status='pending').count()
        context['confirmed_count'] = user_bookings.filter(status='confirmed').count()
        context['cancelled_count'] = user_bookings.filter(status='cancelled').count()
        return context


class BookingCreateView(LoginRequiredMixin, CreateView):
    """创建预约视图"""
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_create.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['room'] = self.get_room()
        return kwargs
    
    def get_room(self):
        return get_object_or_404(StudyRoom, pk=self.kwargs['room_id'], is_active=True)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.room = self.get_room()
        
        # 检查时间段是否已被预约
        existing_booking = Booking.objects.filter(
            room=form.instance.room,
            time_slot=form.instance.time_slot,
            date=form.instance.date,
            status__in=['pending', 'confirmed']
        ).exists()
        
        if existing_booking:
            messages.error(self.request, '该时间段已被预约，请选择其他时间段')
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        
        # 记录预约历史        
        BookingHistory.objects.create(
            booking=self.object,
            action='创建预约',
            operator=self.request.user,
            notes=f'用户{self.request.user.username}创建了预约'
        )
        
        messages.success(self.request, '预约申请提交成功，请等待管理员审核')
        return response
    
    def get_success_url(self):
        return reverse('bookings:booking_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = self.get_room()
        context['time_slots'] = TimeSlot.objects.filter(is_active=True).order_by('start_time')
        context['today'] = timezone.now().date()
        return context


class BookingDetailView(LoginRequiredMixin, DetailView):
    """预约详情视图"""
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        # 普通用户只能查看自己的预约，管理员可以查看所有预约
        if self.request.user.user_type == 'admin' or self.request.user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking_histories'] = BookingHistory.objects.filter(
            booking=self.object
        ).order_by('-created_at')
        return context


class BookingCancelView(LoginRequiredMixin, View):
    """取消预约视图"""
    def get(self, request, pk):
        # GET请求直接取消
        return self.cancel_booking(request, pk)
    
    def post(self, request, pk):
        # POST请求也支持取消
        return self.cancel_booking(request, pk)
    
    def cancel_booking(self, request, pk):
        booking = get_object_or_404(
            Booking, 
            pk=pk, 
            user=request.user,
            status__in=['pending', 'confirmed']
        )
        
        booking.status = 'cancelled'
        booking.save()
        
        # 记录预约历史
        BookingHistory.objects.create(
            booking=booking,
            action='取消预约',
            operator=request.user,
            notes=f'用户{request.user.username}取消了预约'
        )
        
        messages.success(request, '预约已取消')
        return redirect('bookings:booking_list')


class AdminRequiredMixin(UserPassesTestMixin):
    """管理员权限验证"""
    def test_func(self):
        return (self.request.user.is_authenticated and 
                (self.request.user.user_type == 'admin' or self.request.user.is_superuser))


class AdminBookingListView(AdminRequiredMixin, ListView):
    """管理员预约列表视图"""
    model = Booking
    template_name = 'bookings/admin_booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20
    def get_queryset(self):
        queryset = Booking.objects.select_related('room', 'time_slot', 'user').all().order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(room__name__icontains=search) |
                Q(purpose__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 添加统计数据
        all_bookings = Booking.objects.all()
        context['total_bookings'] = all_bookings.count()
        context['pending_count'] = all_bookings.filter(status='pending').count()
        context['confirmed_count'] = all_bookings.filter(status='confirmed').count()
        context['cancelled_count'] = all_bookings.filter(status='cancelled').count()
        
        # 添加自习室列表用于过滤
        context['rooms'] = StudyRoom.objects.filter(is_active=True)
        
        # 添加过滤参数
        context['status_filter'] = self.request.GET.get('status', 'all')
        context['search'] = self.request.GET.get('search', '')
        
        return context


class BookingApproveView(AdminRequiredMixin, View):
    """预约审批视图"""
    def get(self, request, pk):
        # GET请求默认为批准
        return self.handle_booking_action(request, pk, 'approve')
    
    def post(self, request, pk):
        action = request.POST.get('action', 'approve')
        return self.handle_booking_action(request, pk, action)
    
    def handle_booking_action(self, request, pk, action):
        booking = get_object_or_404(Booking, pk=pk)
        notes = request.POST.get('notes', '') if request.method == 'POST' else ''
        
        if action == 'approve':
            booking.status = 'confirmed'
            action_text = '审批通过'
            message = '预约已审批通过'
        elif action == 'reject':
            booking.status = 'cancelled'
            action_text = '审批拒绝'
            message = '预约已被拒绝'
        else:
            messages.error(request, '无效的操作')
            return redirect(reverse('bookings:admin_booking_list'))
        booking.save()
        
        # 记录预约历史
        BookingHistory.objects.create(
            booking=booking,
            action=action_text,
            operator=request.user,
            notes=notes or f'管理员{request.user.username}{action_text}了预约'
        )
        
        messages.success(request, message)
        return redirect(reverse('bookings:admin_booking_list'))
