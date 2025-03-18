from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Scene, Template, TemplateComment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username', 'email')

class SceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scene
        fields = ('id', 'name', 'description', 'created_at', 'updated_at', 'creator', 'tags')
        read_only_fields = ('id', 'created_at', 'updated_at', 'creator')

class TemplateCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TemplateComment
        fields = ('id', 'user', 'content', 'rating', 'created_at')
        read_only_fields = ('id', 'created_at')

class TemplateSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    comments = TemplateCommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = (
            'id', 'name', 'description', 'category', 'content', 'usage',
            'example', 'creator', 'created_at', 'updated_at', 'tags',
            'rating', 'usage_count', 'comments', 'comment_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'creator', 'rating', 'usage_count')

    def get_comment_count(self, obj):
        return obj.comments.count()