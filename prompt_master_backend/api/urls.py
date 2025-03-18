from django.urls import path
from .views import (
    RegisterView, LoginView, UserProfileView, RecommendedScenesView,
    TemplateListView, TemplateDetailView, TemplateUseView, TemplateCommentView,
    RecommendedTemplatesView, TemplateAnalyticsView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
    path('scenes/recommended/', RecommendedScenesView.as_view(), name='recommended-scenes'),
    
    # 模板相关的URL
    path('templates/', TemplateListView.as_view(), name='template-list'),
    path('templates/<int:pk>/', TemplateDetailView.as_view(), name='template-detail'),
    path('templates/<int:pk>/use/', TemplateUseView.as_view(), name='template-use'),
    path('templates/<int:pk>/comments/', TemplateCommentView.as_view(), name='template-comment'),
    path('templates/recommended/', RecommendedTemplatesView.as_view(), name='recommended-templates'),
    path('templates/analytics/', TemplateAnalyticsView.as_view(), name='template-analytics'),
]