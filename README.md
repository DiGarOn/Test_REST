# ToDo List API

Это REST API для управления списком задач, разработанное с использованием Django REST Framework и PostgreSQL. В проекте реализованы следующие функции:

- CRUD операции для задач (ToDo list)
- Аутентификация с использованием JWT
- Добавление комментариев и прикрепление файлов к задачам
- Сортировка и поиск задач
- Автоматическая документация API с помощью drf-spectacular
- Обработка ошибок с единообразным форматированием

## Требования

- Python 3.8+
- PostgreSQL
- [pip](https://pip.pypa.io/en/stable/) или другой менеджер пакетов Python

## Установка

1. **Клонируйте репозиторий:**

    ```bash
    git clone https://github.com/your_username/todo-api.git
    cd todo-api
    ```
2. **Создайте и активируйте виртуальное окружение:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # для macOS и Linux
    # Windows:
    # venv\Scripts\activate
    ```
3. **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```
    Если файл `requirements.txt` отсутствует, установите зависимости вручную:
    ```bash
    pip install django djangorestframework psycopg2-binary drf-spectacular djangorestframework-simplejwt
    ```
4. **Настройте базу данных PostgreSQL:**
    Создайте новую базу данных, например `todo_db`, и настройте параметры подключения в файле `todo_project/settings.py`:
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'todo_db',
            'USER': 'your_db_user',
            'PASSWORD': 'your_db_password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```
## Применение миграций
1. **Выполните миграции:**
    ```bash
    python manage.py migrate
    ```
2. **(Опционально) Создайте суперпользователя для доступа в админку:**
    ```bash
    python manage.py createsuperuser
    ```
## Запуск сервера разработки
Запустите сервер:
```bash
python manage.py runserver
```
Откройте браузер и перейдите по адресу: http://127.0.0.1:8000/

## API и Документация
### Работа с API
- Аутентификация:
    - Получение JWT токенов:
        - `POST /auth/register/` - для создание акканта и корректной работы ручки `login`
        - `POST /auth/login/` — для получения `access` и `refresh` токенов.
        - `POST /auth/login/refresh/` — для обновления access токена.
- Задачи:
    - `GET /api/tasks/` — получить список задач (поддерживается сортировка и поиск, выдает комментарии и файлы связанные с этой задачей).
    - `POST /api/tasks/` — создать новую задачу.
    - `GET /api/tasks/{id}/` — получить информацию о задаче.
    - `PUT /api/tasks/{id}/` — обновить задачу.
    - `PATCH /api/tasks/{id}/` — частично обновить задачу.
    - `DELETE /api/tasks/{id}/` — удалить задачу.
- Комментарии:
    - `GET /api/comments/` — получить список комментариев.
    - `POST /api/comments/` — добавить комментарий к задаче.
- Файлы:
    - `GET /api/files/` — получить список файлов.
    - `POST /api/files/` — прикрепить файл к задаче (multipart/form-data).
### Документация с Swagger UI
API документируется автоматически с использованием drf-spectacular. После запуска сервера вы можете открыть следующие URL:

- Схема OpenAPI (JSON): http://127.0.0.1:8000/schema/
- Swagger UI: http://127.0.0.1:8000/swagger/

## Тестирование
Для запуска unit-тестов выполните команду:

```bash
python manage.py test
```
Тесты покрывают основные функции API: создание, обновление, удаление задач, а также работу с комментариями и файлами.

## Обработка ошибок
В проекте реализована единообразная обработка ошибок с использованием кастомного обработчика исключений, который возвращает подробный JSON-ответ с кодом ошибки и сообщением. Для проверки:

- Отправьте некорректный запрос (например, POST без обязательного поля) и убедитесь, что сервер возвращает статус 400 Bad Request с подробностями ошибки.
