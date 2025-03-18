from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Template, TemplateComment, TemplateUsage
from django.utils import timezone
import random
from datetime import timedelta
from faker import Faker

User = get_user_model()
fake = Faker(['zh_CN'])  # 使用中文数据

class Command(BaseCommand):
    help = 'Generates test data for the PromptMaster application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating test data...')

        # Create test users
        users = self.create_users()
        self.stdout.write('Created users')

        # Create test templates
        templates = self.create_templates(users)
        self.stdout.write('Created templates')

        # Create template comments
        self.create_template_comments(users, templates)
        self.stdout.write('Created comments')

        # Create template usage data
        self.create_template_usage(users, templates)
        self.stdout.write('Created usage data')

        self.stdout.write(self.style.SUCCESS('Successfully generated test data'))

    def create_users(self):
        users = []
        for i in range(20):
            username = f"{fake.last_name()}{fake.first_name()}"
            email = fake.email()
            user, created = User.objects.get_or_create(username=username, email=email)
            if created:
                user.set_password('testpass123')
                user.first_name = fake.first_name()
                user.last_name = fake.last_name()
                user.save()
            users.append(user)
        return users

    def create_templates(self, users):
        categories = {
            'analysis': ['数据分析', '数据可视化', '数据清洗', '统计分析', '预测模型'],
            'writing': ['文案创作', '内容编辑', '广告文案', '新闻写作', '技术文档'],
            'coding': ['代码生成', 'API开发', '单元测试', '代码重构', '性能优化'],
            'marketing': ['营销策划', '社媒运营', '品牌推广', '用户增长', '市场分析']
        }
        
        templates = []
        template_types = {
            'analysis': [
                '数据分析报告模板', '数据可视化脚本', '数据清洗工具',
                '统计分析模型', '预测分析模板', '数据挖掘流程'
            ],
            'writing': [
                '产品描述模板', '新闻稿模板', '社媒文案模板',
                '技术文档模板', '营销文案模板', '用户指南模板'
            ],
            'coding': [
                'API文档生成', '代码注释模板', '单元测试模板',
                '性能优化建议', '代码审查清单', '错误处理模板'
            ],
            'marketing': [
                '营销活动策划', '用户画像分析', '竞品分析报告',
                '市场调研模板', '品牌推广方案', '增长策略模板'
            ]
        }

        for i in range(100):
            category = random.choice(list(categories.keys()))
            template_type = random.choice(template_types[category])
            tags = random.sample(categories[category], random.randint(2, 4))
            
            template = Template.objects.create(
                name=f"{template_type}-{fake.company_prefix()}版",
                description=f"{fake.sentence()}这是一个{template_type}，{fake.sentence()}",
                category=category,
                content=self.generate_template_content(category),
                usage=f"适用场景：{fake.paragraph()}\n使用步骤：\n1. {fake.sentence()}\n2. {fake.sentence()}\n3. {fake.sentence()}",
                example=self.generate_example_content(category),
                creator=random.choice(users),
                tags=tags,
                rating=round(random.uniform(3.5, 5), 1),  # 大多数模板评分在3.5-5之间
                usage_count=random.randint(100, 10000)
            )
            templates.append(template)

        return templates

    def generate_template_content(self, category):
        if category == 'analysis':
            return f"""# {fake.company()}数据分析报告模板

## 1. 数据概览
{fake.paragraph()}

## 2. 分析方法
- {fake.sentence()}
- {fake.sentence()}
- {fake.sentence()}

## 3. 关键发现
1. {fake.sentence()}
2. {fake.sentence()}
3. {fake.sentence()}

## 4. 建议
{fake.paragraph()}"""
        elif category == 'writing':
            return f"""# {fake.company_prefix()}{fake.word()}产品文案

## 产品亮点
1. {fake.sentence()}
2. {fake.sentence()}
3. {fake.sentence()}

## 目标用户
{fake.paragraph()}

## 核心信息
{fake.paragraph()}

## 号召性用语
- {fake.sentence()}
- {fake.sentence()}"""
        elif category == 'coding':
            return f"""/**
 * {fake.sentence()}
 * 
 * @param {fake.word()} - {fake.sentence()}
 * @param {fake.word()} - {fake.sentence()}
 * @returns {fake.sentence()}
 */
function {fake.word()}({fake.word()}, {fake.word()}) {{
    // TODO: 实现具体功能
    {fake.sentence()}
}}

// 使用示例
{fake.sentence()}
"""
        else:  # marketing
            return f"""# {fake.company()}营销方案

## 市场分析
{fake.paragraph()}

## 目标人群
{fake.paragraph()}

## 营销策略
1. {fake.sentence()}
2. {fake.sentence()}
3. {fake.sentence()}

## 预期效果
{fake.paragraph()}"""

    def generate_example_content(self, category):
        if category == 'analysis':
            return f"""## 数据分析结果示例

1. 数据趋势
{fake.paragraph()}

2. 关键指标
- {fake.sentence()}
- {fake.sentence()}

3. 结论
{fake.paragraph()}"""
        elif category == 'writing':
            return f"""## 文案示例

标题：{fake.sentence()}

正文：
{fake.paragraph()}

关键词：{fake.word()}、{fake.word()}、{fake.word()}"""
        elif category == 'coding':
            return f"""// 代码示例
const {fake.word()} = {{
    name: '{fake.word()}',
    description: '{fake.sentence()}'
}};

// 输出结果
{fake.sentence()}"""
        else:  # marketing
            return f"""## 营销方案示例

活动名称：{fake.sentence()}

执行步骤：
1. {fake.sentence()}
2. {fake.sentence()}

预期结果：
{fake.paragraph()}"""

    def create_template_comments(self, users, templates):
        comment_templates = [
            "这个模板{verb}，{detail}",
            "{verb}这个模板，{detail}",
            "模板整体{verb}，{detail}",
            "{verb}，{detail}，推荐使用。",
            "使用效果{verb}，{detail}"
        ]
        
        verbs = ['非常实用', '很专业', '很全面', '很贴心', '设计合理', '效果显著']
        details = [
            '对工作帮助很大',
            '节省了很多时间',
            '内容很专业',
            '逻辑性强',
            '可以直接使用',
            '值得推荐',
            '适合新手使用',
            '专业度高',
            '效果明显',
            '使用体验好'
        ]

        for template in templates:
            # 根据模板的使用次数决定评论数量
            comment_count = random.randint(5, 20)
            for _ in range(comment_count):
                comment_template = random.choice(comment_templates)
                verb = random.choice(verbs)
                detail = random.choice(details)
                
                rating = random.choices(
                    [5, 4, 3, 2, 1],
                    weights=[0.5, 0.3, 0.15, 0.04, 0.01]  # 大多数评分在4-5星
                )[0]
                
                TemplateComment.objects.create(
                    template=template,
                    user=random.choice(users),
                    content=comment_template.format(verb=verb, detail=detail),
                    rating=rating
                )

    def create_template_usage(self, users, templates):
        end_date = timezone.now()
        start_date = end_date - timedelta(days=180)

        # 为每个模板创建使用记录
        for template in templates:
            # 根据模板的总使用次数创建详细记录
            usage_count = template.usage_count
            for _ in range(usage_count):
                user = random.choice(users)
                used_at = fake.date_time_between(
                    start_date=start_date,
                    end_date=end_date,
                    tzinfo=timezone.get_current_timezone()
                )
                
                context = {
                    'input_params': {
                        'scenario': fake.word(),
                        'requirements': fake.sentence(),
                        'additional_info': fake.sentence()
                    },
                    'duration': random.randint(30, 300),  # 使用时长（秒）
                    'success': random.random() > 0.1  # 90%的成功率
                }
                
                TemplateUsage.objects.create(
                    template=template,
                    user=user,
                    used_at=used_at,
                    context=context
                )