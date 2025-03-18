from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    # Add custom fields for the user model here
    pass

class Scene(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scenes')
    tags = models.JSONField(default=list)

    def __str__(self):
        return self.name

class Template(models.Model):
    CATEGORY_CHOICES = [
        ('analysis', '数据分析'),
        ('writing', '文案创作'),
        ('coding', '代码开发'),
        ('marketing', '营销策划'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    content = models.TextField()
    usage = models.TextField()
    example = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.JSONField(default=list)
    rating = models.FloatField(default=0)
    usage_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class TemplateComment(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.template.name} by {self.user.username}"

class PromptTemplate(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prompt_templates')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    tags = models.JSONField(default=list)
    version = models.IntegerField(default=1)
    
    def __str__(self):
        return self.name

class TemplateUsage(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)
    context = models.JSONField(default=dict)  # 存储使用时的上下文信息

    class Meta:
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.user.username} used {self.template.name} at {self.used_at}"