# tasks/exceptions.py
from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений. Вызывается для каждого исключения, 
    возникшего во view.
    """
    # Вызов стандартного обработчика DRF
    response = exception_handler(exc, context)
    
    # Добавляем логирование
    if response is not None:
        logger.error(
            f"Exception occurred in {context.get('view')} - {exc}",
            exc_info=True
        )
        # Пример: можно добавить общий формат ответа для ошибок:
        custom_response_data = {
            'status_code': response.status_code,
            'errors': response.data,
            'detail': 'Произошла ошибка. Обратитесь к документации API.'
        }
        response.data = custom_response_data

    return response
