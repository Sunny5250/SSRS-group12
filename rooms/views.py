from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import StudyRoom, TimeSlot


class RoomListView(LoginRequiredMixin, ListView):
    """自习室列表视图
    
    显示所有活跃的自习室列表，支持搜索功能。
    继承LoginRequiredMixin确保只有登录用户可以访问。
    """
    model = StudyRoom  # 使用StudyRoom模型
    template_name = 'rooms/room_list.html'  # 指定模板文件
    context_object_name = 'rooms'  # 在模板中使用的变量名
    paginate_by = 12  # 每页显示12个自习室
    
    def get_queryset(self):
        """
        获取查询集
        
        返回所有活跃的自习室，并根据搜索条件过滤结果。
        支持按名称、位置和描述进行模糊搜索。
        """
        queryset = StudyRoom.objects.filter(is_active=True)  # 只获取活跃的自习室
        search = self.request.GET.get('search')  # 获取搜索参数
        if search:
            # 使用Q对象实现OR查询，搜索名称、位置或描述中包含搜索词的自习室
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.order_by('name')  # 按名称排序结果
    
    def get_context_data(self, **kwargs):
        """
        获取上下文数据
        
        添加搜索词到上下文，用于在模板中回显搜索条件。
        """
        context = super().get_context_data(**kwargs)  # 获取父类上下文
        context['search'] = self.request.GET.get('search', '')  # 添加搜索词到上下文
        return context


class RoomDetailView(LoginRequiredMixin, DetailView):
    """自习室详情视图
    
    显示单个自习室的详细信息。
    继承LoginRequiredMixin确保只有登录用户可以访问。
    """
    model = StudyRoom  # 使用StudyRoom模型
    template_name = 'rooms/room_detail.html'  # 指定模板文件
    context_object_name = 'room'  # 在模板中使用的变量名
    
    def get_context_data(self, **kwargs):
        """
        获取上下文数据
        
        添加时间段列表到上下文，用于预约时间选择。
        """
        context = super().get_context_data(**kwargs)  # 获取父类上下文
        context['time_slots'] = TimeSlot.objects.filter(is_active=True).order_by('start_time')  # 添加可用时间段
        return context
