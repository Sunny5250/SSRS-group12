from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """自定义用户注册表单"""
    email = forms.EmailField(required=True, label='邮箱')
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        label='用户类型'
    )
    phone = forms.CharField(max_length=11, required=False, label='手机号')
    student_id = forms.CharField(max_length=20, required=False, label='学号/工号')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'user_type', 'phone', 'student_id', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = self.cleaned_data['user_type']
        user.phone = self.cleaned_data['phone']
        user.student_id = self.cleaned_data['student_id']
        if commit:
            user.save()
        return user


class RegisterView(CreateView):
    """用户注册视图"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('rooms:room_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, '注册成功，欢迎使用自习室预约系统！')
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    """用户资料视图"""
    model = User
    fields = ['first_name', 'last_name', 'email', 'phone', 'student_id', 'avatar']
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, '个人信息更新成功！')
        return super().form_valid(form)
