from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自定义用户模型
    
    继承自Django的AbstractUser，扩展了用户类型、手机号、学号/工号、头像等字段
    支持学生、教师、管理员三种用户类型
    """
    
    # 用户类型选择项
    USER_TYPE_CHOICES = [
        ('student', '学生'),    # 学生用户
        ('teacher', '教师'),    # 教师用户  
        ('admin', '管理员'),    # 管理员用户
    ]
    
    # 用户类型字段
    user_type = models.CharField(
        max_length=10,                    # 最大长度10个字符
        choices=USER_TYPE_CHOICES,        # 限制选择范围
        default='student',                # 默认为学生类型
        verbose_name='用户类型',          # 字段显示名称
        help_text='用户在系统中的角色类型'  # 字段帮助文本
    )
    
    # 手机号字段
    phone = models.CharField(
        max_length=11,                    # 手机号最大11位
        blank=True,                       # 表单中可以为空
        null=True,                        # 数据库中可以为NULL
        verbose_name='手机号',            # 字段显示名称
        help_text='用户的联系电话'         # 字段帮助文本
    )
    
    # 学号/工号字段
    student_id = models.CharField(
        max_length=20,                    # 最大长度20个字符
        blank=True,                       # 表单中可以为空
        null=True,                        # 数据库中可以为NULL
        verbose_name='学号/工号',         # 字段显示名称
        help_text='学生的学号或教师的工号'  # 字段帮助文本
    )
    
    # 头像字段
    avatar = models.ImageField(
        upload_to='avatars/',             # 上传到avatars目录
        blank=True,                       # 表单中可以为空
        null=True,                        # 数据库中可以为NULL
        verbose_name='头像',              # 字段显示名称
        help_text='用户头像图片'           # 字段帮助文本
    )
    
    # 创建时间字段
    created_at = models.DateTimeField(
        auto_now_add=True,                # 创建时自动设置当前时间
        verbose_name='创建时间',          # 字段显示名称
        help_text='用户账户创建的时间'     # 字段帮助文本
    )
    
    # 更新时间字段
    updated_at = models.DateTimeField(
        auto_now=True,                    # 每次保存时自动更新为当前时间
        verbose_name='更新时间',          # 字段显示名称
        help_text='用户信息最后更新的时间' # 字段帮助文本
    )
    
    class Meta:
        """模型元数据配置"""
        verbose_name = '用户'             # 单数显示名称
        verbose_name_plural = '用户'      # 复数显示名称
        db_table = 'accounts_user'        # 数据库表名（可选）
        ordering = ['-created_at']        # 默认按创建时间倒序排列
    
    def __str__(self):
        """
        字符串表示方法
        
        Returns:
            str: 返回用户名和用户类型的组合字符串
        """
        return f"{self.username} ({self.get_user_type_display()})"
    
    def is_student(self):
        """
        判断是否为学生用户
        
        Returns:
            bool: 如果是学生返回True，否则返回False
        """
        return self.user_type == 'student'
    
    def is_teacher(self):
        """
        判断是否为教师用户
        
        Returns:
            bool: 如果是教师返回True，否则返回False
        """
        return self.user_type == 'teacher'
    
    def is_admin_user(self):
        """
        判断是否为管理员用户
        
        Returns:
            bool: 如果是管理员返回True，否则返回False
        """
        return self.user_type == 'admin'
    
    def get_display_name(self):
        """
        获取用户显示名称
        
        Returns:
            str: 优先返回first_name + last_name，如果为空则返回username
        """
        if self.first_name and self.last_name:
            return f"{self.last_name}{self.first_name}"
        return self.username
