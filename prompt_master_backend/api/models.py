from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    自定义用户模型
    扩展Django的AbstractUser，添加额外的字段
    """
    email = models.EmailField(unique=True)  # 将email设置为唯一
    avatar = models.URLField(max_length=500, blank=True)  # 用户头像
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间

    class Meta:
        db_table = 'users'  # 指定表名
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username