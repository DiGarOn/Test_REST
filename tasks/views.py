from rest_framework import viewsets, permissions, filters
from .models import Task, Comment, File
from .serializers import TaskSerializer, CommentSerializer, FileSerializer

class TaskViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']  # Явно разрешаем PUT
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Подключаем фильтры сортировки и поиска
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    # Разрешаем сортировку по дате создания и статусу
    ordering_fields = ['created_at', 'status']
    # Реализуем поиск по названию и описанию задачи
    search_fields = ['title', 'description']

    def get_queryset(self):
        status = self.request.query_params.get('status', None)
        if status:
            return Task.objects.filter(status=status)
        return Task.objects.all()

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]
