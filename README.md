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

### Базовая настройка

Создайте файл `log_config.py` для инициализации основного логгера:

```python
from profi_log import MasterLogger

# Инициализация основного логгера
master_logger = MasterLogger("app.log", level="INFO")
master_logger.setup_colored_console_logging()
```

### Использование в разных модулях

В файле `main.py`:

```python
from log_config import master_logger

# Получаем логгер для main.py
logger = master_logger.get_logger('main')

def main():
    logger.info("Начало выполнения программы")
    # Ваш код здесь
    logger.info("Программа завершена")

if __name__ == "__main__":
    main()
```

В файле `utils.py`:

```python
from log_config import master_logger

# Получаем логгер для utils.py
logger = master_logger.get_logger('utils')

@master_logger.log_function_call()
def process_data(data):
    logger.info(f"Начало обработки данных: {data}")
    result = sum(data)
    logger.debug(f"Промежуточный результат: {result}")
    return result * 2
```

### Дополнительные возможности

```python
# Временное изменение уровня логирования
with master_logger.temporary_log_level("DEBUG"):
    logger.debug("Это отладочное сообщение")

# Логирование исключений
try:
    1 / 0
except ZeroDivisionError:
    logger.log_exception("Произошла ошибка деления на ноль")
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
