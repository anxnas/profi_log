# Profi Log

Profi Log - это продвинутая библиотека для логирования в Python, предоставляющая расширенные возможности и гибкую настройку логирования.

## Возможности

- Файловое логирование с ротацией логов
- Цветное консольное логирование
- Отправка критических логов по email
- Временное изменение уровня логирования
- Логирование исключений с полной трассировкой стека
- Автоматическое логирование вызовов функций

## Установка

Установите Profi Log с помощью pip:

```sh
pip install profi_log
```

## Использование

Вот простой пример использования Profi Log:

```python
from profi_log import MasterLogger
#Инициализация логгера
logger = MasterLogger("app.log", level="DEBUG")
#Настройка цветного консольного логирования
logger.setup_colored_console_logging()
#Использование логгера
logger.info("Это информационное сообщение")
logger.warning("Это предупреждение")
logger.error("Это сообщение об ошибке")
#Использование временного уровня логирования
with logger.temporary_log_level("DEBUG"):
    logger.debug("Это отладочное сообщение")
#Логирование исключений
try:
    1 / 0
except ZeroDivisionError:
    logger.log_exception("Произошла ошибка деления на ноль")
#Использование декоратора для логирования вызовов функций
@logger.log_function_call()
def example_function(x, y):
    return x + y
result = example_function(3, 4)
```

## Документация

Подробную документацию можно найти [здесь](https://anxnas.github.io/profi_log/).

## Разработка

Для настройки среды разработки:

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/anxnas/profi_log.git
   ```
2. Перейдите в директорию проекта:
   ```
   cd profi_log
   ```

## Вклад в проект

Я приветствую вклад в развитие Profi Log! Пожалуйста, напишите мне [на почту](mailto:slavakhrenov02@gmail.com) перед тем, как отправлять pull request.

## Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## Автор

Святослав Хренов - anxnas