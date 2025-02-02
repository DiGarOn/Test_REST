from rest_framework import serializers
from .models import Task, Comment, File

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    files = FileSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = '__all__'
