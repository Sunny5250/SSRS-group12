# Django内置模块导入
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django import forms

# 自定义模型导入
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    自定义用户注册表单
    
    继承自Django的UserCreationForm，扩展了邮箱、用户类型、手机号、学号/工号等字段
    用于用户注册时收集必要信息
    """
    
    # 扩展的字段定义
    email = forms.EmailField(
        required=True,                    # 必填字段
        label='邮箱',                     # 表单显示标签
        help_text='请输入有效的邮箱地址'    # 帮助文本
    )
    
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,   # 使用User模型中定义的用户类型选项
        label='用户类型',                  # 表单显示标签
        help_text='请选择您的用户类型'      # 帮助文本
    )
    
    phone = forms.CharField(
        max_length=11,                    # 最大长度11位
        required=False,                   # 非必填字段
        label='手机号',                    # 表单显示标签
        help_text='请输入11位手机号码'      # 帮助文本
    )
    
    student_id = forms.CharField(
        max_length=20,                    # 最大长度20位
        required=False,                   # 非必填字段
        label='学号/工号',                # 表单显示标签
        help_text='学生请输入学号，教师请输入工号'  # 帮助文本
    )
    
    class Meta:
        """表单元数据配置"""
        model = User                      # 关联的模型
        fields = (                        # 表单字段顺序
            'username',                   # 用户名
            'email',                      # 邮箱
            'user_type',                  # 用户类型
            'phone',                      # 手机号
            'student_id',                 # 学号/工号
            'password1',                  # 密码
            'password2'                   # 确认密码
        )
    
    def save(self, commit=True):
        """
        保存表单数据到用户模型
        
        Args:
            commit (bool): 是否立即保存到数据库
            
        Returns:
            User: 保存的用户对象
        """
        user = super().save(commit=False)  # 创建用户对象但不保存
        # 设置用户属性
        user.email = self.cleaned_data['email']
        user.user_type = self.cleaned_data['user_type']
        user.phone = self.cleaned_data['phone']
        user.student_id = self.cleaned_data['student_id']
        
        if commit:
            user.save()  # 保存到数据库
        return user


class RegisterView(CreateView):
    """
    用户注册视图
    
    处理用户注册请求，注册成功后自动登录并跳转到自习室列表页面
    """
    
    form_class = CustomUserCreationForm   # 使用的表单类
    template_name = 'accounts/register.html'  # 模板文件路径
    success_url = reverse_lazy('rooms:room_list')  # 注册成功后的跳转URL
    
    def form_valid(self, form):
        """
        表单验证通过后的处理
        
        Args:
            form: 验证通过的表单对象
            
        Returns:
            HttpResponse: 响应对象
        """
        response = super().form_valid(form)  # 调用父类的处理方法
        login(self.request, self.object)     # 自动登录新注册的用户
        messages.success(self.request, '注册成功，欢迎使用自习室预约系统！')  # 显示成功消息
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    用户资料视图
    
    处理用户个人资料的查看和更新，需要用户登录才能访问
    继承自LoginRequiredMixin确保只有登录用户才能访问
    """
    
    model = User                          # 关联的模型
    fields = [                            # 可编辑的字段
        'first_name',                     # 名
        'last_name',                      # 姓
        'email',                          # 邮箱
        'phone',                          # 手机号
        'student_id',                     # 学号/工号
        'avatar'                          # 头像
    ]
    template_name = 'accounts/profile.html'  # 模板文件路径
    success_url = reverse_lazy('accounts:profile')  # 更新成功后的跳转URL
    
    def get_object(self):
        """
        获取要编辑的对象
        
        Returns:
            User: 当前登录的用户对象
        """
        return self.request.user
    
    def form_valid(self, form):
        """
        表单验证通过后的处理
        
        Args:
            form: 验证通过的表单对象
            
        Returns:
            HttpResponse: 响应对象
        """
        messages.success(self.request, '个人信息更新成功！')  # 显示成功消息
        return super().form_valid(form)  # 调用父类的处理方法
