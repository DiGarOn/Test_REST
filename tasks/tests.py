import io
import tempfile
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Task, Comment, File

User = get_user_model()


class BaseAPITestCase(APITestCase):
    """
    Базовый класс тестов, который создаёт пользователя и настраивает аутентификацию.
    """
    def setUp(self):
        # Создаём тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        # Принудительно аутентифицируем пользователя для тестов
        self.client.force_authenticate(user=self.user)


class TaskAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        # URL для списка задач
        self.tasks_url = reverse('task-list')  # Если используется DefaultRouter и basename=tasks, иначе используйте прямой путь

    def test_create_task(self):
        """
        Тест создания новой задачи.
        """
        payload = {
            "title": "Новая задача",
            "description": "Описание задачи",
            "status": "новая"
        }
        response = self.client.post(self.tasks_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], payload['title'])
        self.assertEqual(response.data['status'], payload['status'])

    def test_get_tasks_list(self):
        """
        Тест получения списка задач с пагинацией.
        """
        # Создадим несколько задач
        for i in range(15):
            Task.objects.create(title=f"Task {i}", status="новая")
        
        response = self.client.get(self.tasks_url)
        # Если у вас настроена пагинация, проверяем наличие ключа 'results'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertTrue(len(response.data['results']) <= 10)  # если лимит по умолчанию 10

    def test_filter_tasks_by_status(self):
        """
        Тест фильтрации задач по статусу.
        """
        Task.objects.create(title="Task 1", status="новая")
        Task.objects.create(title="Task 2", status="в работе")
        
        # Передаём статус "новая" в качестве фильтра
        response = self.client.get(self.tasks_url, {'status': 'новая'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что все задачи в ответе имеют статус "новая"
        for task in response.data.get('results', response.data):
            self.assertEqual(task['status'], 'новая')

    def test_retrieve_task(self):
        """
        Тест получения задачи по её id.
        """
        task = Task.objects.create(title="Task detail", status="новая")
        detail_url = reverse('task-detail', kwargs={'pk': task.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(task.id))

    def test_update_task_put(self):
        """
        Тест обновления задачи через PUT.
        """
        task = Task.objects.create(title="Old Title", status="новая")
        detail_url = reverse('task-detail', kwargs={'pk': task.id})
        payload = {
            "title": "Updated Title",
            "description": "Обновленное описание",
            "status": "в работе"
        }
        response = self.client.put(detail_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, payload['title'])
        self.assertEqual(task.status, payload['status'])

    def test_partial_update_task_patch(self):
        """
        Тест частичного обновления задачи через PATCH.
        """
        task = Task.objects.create(title="Task", status="новая")
        detail_url = reverse('task-detail', kwargs={'pk': task.id})
        payload = {"status": "выполнена"}
        response = self.client.patch(detail_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, payload['status'])

    def test_delete_task(self):
        """
        Тест удаления задачи.
        """
        task = Task.objects.create(title="Task to delete", status="новая")
        detail_url = reverse('task-detail', kwargs={'pk': task.id})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_sort_tasks(self):
        """
        Тест сортировки задач по дате создания и статусу.
        Допустим, у нас в API есть возможность передавать параметры сортировки, например:
        ?ordering=created_at или ?ordering=status
        """
        task1 = Task.objects.create(title="Task 1", status="новая")
        task2 = Task.objects.create(title="Task 2", status="в работе")
        # Пример запроса на сортировку по дате создания (от более ранней к поздней)
        response = self.client.get(self.tasks_url, {'ordering': 'created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = response.data.get('results', response.data)
        self.assertGreaterEqual(len(tasks), 2)
        # Проверка сортировки по статусу (при условии, что такой функционал реализован)
        response_status = self.client.get(self.tasks_url, {'ordering': 'status'})
        self.assertEqual(response_status.status_code, status.HTTP_200_OK)


class CommentAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        # Создадим задачу для тестирования комментариев
        self.task = Task.objects.create(title="Task for comments", status="новая")
        self.comments_url = reverse('comment-list')

    def test_create_comment(self):
        """
        Тест создания комментария к задаче.
        """
        payload = {
            "task": str(self.task.id),
            "text": "Это комментарий"
        }
        response = self.client.post(self.comments_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], payload['text'])
        # Проверяем, что комментарий связан с нужной задачей
        self.assertEqual(response.data['task'], str(self.task.id))


class FileAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(title="Task for file", status="новая")
        self.files_url = reverse('file-list')

    def test_upload_file(self):
        """
        Тест прикрепления файла к задаче.
        """
        # Создаем временный файл
        temp_file = tempfile.NamedTemporaryFile(suffix=".txt")
        temp_file.write(b"Containence of test file")
        temp_file.seek(0)

        payload = {
            "task": str(self.task.id),
            "file": temp_file,
        }
        response = self.client.post(self.files_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Проверяем, что файл прикреплён к задаче
        file_obj = File.objects.get(id=response.data['id'])
        self.assertEqual(str(file_obj.task.id), str(self.task.id))
        temp_file.close()

    def test_file_download(self):
        """
        Тест загрузки файла.
        Создаем файл, затем запрашиваем его.
        """
        # Создаем временный файл и сохраняем его через модель
        temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        temp_file.write(b"Test file content")
        temp_file.seek(0)
        temp_file.close()

        file_instance = File.objects.create(task=self.task, file=temp_file.name)
        detail_url = reverse('file-detail', kwargs={'pk': file_instance.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # В ответе могут быть данные файла, например, путь к файлу или метаданные

        # Не забудьте удалить временный файл, если он больше не нужен.


class SearchAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        # Создаём задачи для теста поиска
        Task.objects.create(title="Поиск задача 1", description="Описание первое", status="новая")
        Task.objects.create(title="Еще задача", description="Ничего особенного", status="в работе")
        self.tasks_url = reverse('task-list')

    def test_search_tasks_by_title_and_description(self):
        """
        Тест поиска задач по названию и описанию.
        Допустим, что поиск реализован через передачу параметра `search`.
        """
        response = self.client.get(self.tasks_url, {'search': 'Поиск'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = response.data.get('results', response.data)
        # Ожидаем, что найдется хотя бы одна задача, содержащая слово "Поиск" в заголовке
        self.assertTrue(any("Поиск" in task['title'] for task in tasks))


# Дополнительно можно протестировать обработку ошибок, например:
class ErrorHandlingTests(BaseAPITestCase):
    def test_create_task_without_title(self):
        """
        Тест попытки создания задачи без обязательного поля title.
        """
        payload = {
            "description": "Описание без title",
            "status": "новая"
        }
        response = self.client.post(reverse('task-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
