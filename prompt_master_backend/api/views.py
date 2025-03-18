from rest_framework import generics, permissions, status, filters, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.db.models import Q, Avg, Count, F
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from .serializers import (
    UserSerializer, UserProfileSerializer, SceneSerializer,
    TemplateSerializer, TemplateCommentSerializer, PromptTemplateSerializer
)
from .models import (
    User, Scene, Template, TemplateComment, 
    TemplateUsage, PromptTemplate
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=400)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class RecommendedScenesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 这里应该实现推荐算法，目前我们只返回最新的3个场景
        scenes = Scene.objects.order_by('-created_at')[:3]
        serializer = SceneSerializer(scenes, many=True)
        return Response(serializer.data)

class TemplateListView(generics.ListAPIView):
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'tags']

    def get_queryset(self):
        queryset = Template.objects.all()
        
        # 基本过滤
        category = self.request.query_params.get('category', None)
        if category and category != 'all':
            queryset = queryset.filter(category=category)

        # 高级过滤
        rating = self.request.query_params.get('rating', None)
        if rating:
            queryset = queryset.filter(rating__gte=float(rating))

        usage_count = self.request.query_params.get('usage_count', None)
        if usage_count:
            queryset = queryset.filter(usage_count__gte=int(usage_count))

        # 时间范围过滤
        time_range = self.request.query_params.get('time_range', None)
        if time_range:
            if time_range == 'today':
                queryset = queryset.filter(created_at__date=timezone.now().date())
            elif time_range == 'week':
                queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
            elif time_range == 'month':
                queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))

        # 标签过滤
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                queryset = queryset.filter(tags__contains=[tag])

        # 排序
        sort_by = self.request.query_params.get('sort_by', 'created_at')
        sort_order = self.request.query_params.get('sort_order', 'desc')
        
        order_fields = {
            'created_at': '-created_at' if sort_order == 'desc' else 'created_at',
            'rating': '-rating' if sort_order == 'desc' else 'rating',
            'usage_count': '-usage_count' if sort_order == 'desc' else 'usage_count',
            'name': '-name' if sort_order == 'desc' else 'name'
        }
        
        order_by = order_fields.get(sort_by, '-created_at')
        return queryset.order_by(order_by)

class TemplateDetailView(generics.RetrieveAPIView):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

class TemplateUseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            template = Template.objects.get(pk=pk)
            template.usage_count += 1
            template.save()

            # 记录模板使用情况
            TemplateUsage.objects.create(
                template=template,
                user=request.user,
                context=request.data.get('context', {})
            )

            return Response({'status': 'success'})
        except Template.DoesNotExist:
            return Response(
                {'error': 'Template not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class TemplateCommentView(generics.CreateAPIView):
    serializer_class = TemplateCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        template_id = self.kwargs.get('pk')
        template = Template.objects.get(pk=template_id)
        serializer.save(user=self.request.user, template=template)
        
        # 更新模板的平均评分
        avg_rating = TemplateComment.objects.filter(template=template).aggregate(
            Avg('rating')
        )['rating__avg']
        template.rating = avg_rating or 0
        template.save()

class RecommendedTemplatesView(generics.ListAPIView):
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # 获取用户最近使用的模板类别
        recent_categories = Template.objects.filter(
            templateusage__user=user
        ).values('category').annotate(
            usage_count=Count('id')
        ).order_by('-usage_count')[:3]

        recent_category_ids = [cat['category'] for cat in recent_categories]

        # 获取用户最近使用的标签
        recent_tags = Template.objects.filter(
            templateusage__user=user
        ).values_list('tags', flat=True)
        recent_tags = [tag for tags in recent_tags for tag in tags]
        recent_tags = sorted(set(recent_tags), key=recent_tags.count, reverse=True)[:5]

        # 基于类别、标签和评分推荐模板
        recommended_templates = Template.objects.filter(
            Q(category__in=recent_category_ids) |
            Q(tags__overlap=recent_tags)
        ).exclude(
            templateusage__user=user
        ).order_by('-rating', '-usage_count')[:10]

        return recommended_templates

class PromptTemplateViewSet(viewsets.ModelViewSet):
    queryset = PromptTemplate.objects.all()
    serializer_class = PromptTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'name']

    def get_queryset(self):
        queryset = PromptTemplate.objects.all()
        
        # 搜索
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        # 标签过滤
        tags = self.request.query_params.get('tags', None)
        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                queryset = queryset.filter(tags__contains=[tag])
        
        # 时间范围过滤
        time_range = self.request.query_params.get('time_range', None)
        if time_range:
            if time_range == 'today':
                queryset = queryset.filter(created_at__date=timezone.now().date())
            elif time_range == 'week':
                queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
            elif time_range == 'month':
                queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))
        
        # 排序
        sort_by = self.request.query_params.get('sort_by', 'created_at')
        sort_order = self.request.query_params.get('sort_order', 'desc')
        
        if sort_order == 'desc':
            queryset = queryset.order_by(f'-{sort_by}')
        else:
            queryset = queryset.order_by(sort_by)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class TemplateAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        time_range = request.query_params.get('time_range', 'week')
        if time_range == 'week':
            start_date = timezone.now() - timedelta(days=7)
        elif time_range == 'month':
            start_date = timezone.now() - timedelta(days=30)
        elif time_range == 'quarter':
            start_date = timezone.now() - timedelta(days=90)
        else:
            return Response({'error': 'Invalid time range'}, status=400)

        # 使用趋势数据
        usage_data = TemplateUsage.objects.filter(used_at__gte=start_date) \
            .annotate(date=TruncDate('used_at')) \
            .values('date') \
            .annotate(count=Count('id')) \
            .order_by('date')

        # 分类统计数据
        category_data = Template.objects.values('category') \
            .annotate(count=Count('templateusage', filter=Q(templateusage__used_at__gte=start_date))) \
            .order_by('-count')

        # 热门标签
        popular_tags = Template.objects.filter(templateusage__used_at__gte=start_date) \
            .values('tags') \
            .annotate(count=Count('templateusage')) \
            .order_by('-count')[:20]

        # 使用排行
        top_templates = Template.objects.filter(templateusage__used_at__gte=start_date) \
            .annotate(recent_usage_count=Count('templateusage')) \
            .order_by('-recent_usage_count')[:10]

        serialized_top_templates = TemplateSerializer(top_templates, many=True).data
        for template, serialized_template in zip(top_templates, serialized_top_templates):
            serialized_template['recent_usage_count'] = template.recent_usage_count

        return Response({
            'usageData': {
                'labels': [item['date'].strftime('%Y-%m-%d') for item in usage_data],
                'values': [item['count'] for item in usage_data]
            },
            'categoryData': {
                'labels': [item['category'] for item in category_data],
                'values': [item['count'] for item in category_data]
            },
            'popularTags': [{'name': item['tags'], 'count': item['count']} for item in popular_tags],
            'topTemplates': serialized_top_templates
        })