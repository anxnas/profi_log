import logging
from logging.handlers import RotatingFileHandler
import os
import contextlib
import colorlog
import traceback
import smtplib
from email.message import EmailMessage
import functools


class MasterLogger:
    """
    Продвинутый класс для настройки и управления логированием.
    """

    def __init__(self, log_file_name: str, name: str = None, max_bytes: int = 100 * 1024 * 1024, backup_count: int = 5,
                 encoding: str = 'utf-8', level: str = 'INFO'):
        """
        Инициализация MasterLogger.

        Args:
            log_file_name (str): Имя файла для логов.
            name (str, optional): Имя логгера. Если не указано, используется корневой логгер.
            max_bytes (int): Максимальный размер файла логов в байтах. По умолчанию 100 МБ.
            backup_count (int): Количество резервных копий файлов логов. По умолчанию 5.
            encoding (str): Кодировка файла логов. По умолчанию 'utf-8'.
            level (str): Уровень логирования. По умолчанию 'INFO'.
        """
        self.log_file_name = log_file_name
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.encoding = encoding
        self.level = getattr(logging, level.upper())

        log_dir = os.path.dirname(log_file_name)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self._logger = logging.getLogger(name) if name else logging.getLogger()
        self.setup_file_logging()

    def setup_file_logging(self):
        """
        Настройка логирования в файл.
        """
        handler = RotatingFileHandler(
            self.log_file_name,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding=self.encoding
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(self.level)

    def setup_colored_console_logging(self, format_string: str = None):
        """
        Настройка цветного консольного логирования.

        Args:
            format_string (str, optional): Строка форматирования для логов.
                По умолчанию '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'.
        """
        if format_string is None:
            format_string = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        handler = colorlog.StreamHandler()
        handler.setFormatter(colorlog.ColoredFormatter(
            format_string,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        ))
        self._logger.addHandler(handler)

    def setup_email_logging(self, smtp_server: str, port: int, sender: str, password: str, recipients: list,
                            subject_prefix: str = "Критическая ошибка"):
        """
        Настройка отправки критических логов по электронной почте.

        Args:
            smtp_server (str): SMTP сервер.
            port (int): Порт SMTP сервера.
            sender (str): Email отправителя.
            password (str): Пароль отправителя.
            recipients (list): Список получателей.
            subject_prefix (str, optional): Префикс для темы письма. По умолчанию "Критическая ошибка".
        """

        class EmailHandler(logging.Handler):
            def emit(self, record):
                msg = EmailMessage()
                msg.set_content(self.format(record))
                msg['Subject'] = f"{subject_prefix}: {record.getMessage()}"
                msg['From'] = sender
                msg['To'] = ', '.join(recipients)

                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()
                    server.login(sender, password)
                    server.send_message(msg)

        handler = EmailHandler()
        handler.setLevel(logging.CRITICAL)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    @contextlib.contextmanager
    def temporary_log_level(self, level: str):
        """
        Контекстный менеджер для временного изменения уровня логирования.

        Args:
            level (str): Временный уровень логирования.

        Yields:
            None

        Использование:
        with logger.temporary_log_level('DEBUG'):
            # Здесь логирование будет на уровне DEBUG
        # После выхода из контекста уровень вернется к предыдущему
        """
        old_level = self._logger.level
        self._logger.setLevel(getattr(logging, level.upper()))
        try:
            yield
        finally:
            self._logger.setLevel(old_level)

    def log_exception(self, message: str, exc_info: bool = True):
        """
        Логирование исключения с полной трассировкой стека.

        Args:
            message (str): Сообщение об ошибке.
            exc_info (bool, optional): Флаг для включения информации об исключении. По умолчанию True.

        Использование:
        try:
            # код, который может вызвать исключение
        except Exception as e:
            logger.log_exception("Произошла ошибка")
        """
        if exc_info:
            self._logger.error(f"{message}\n{traceback.format_exc()}")
        else:
            self._logger.error(message)

    def log_function_call(self, log_args: bool = True, log_result: bool = True):
        """
        Декоратор для автоматического логирования вызовов функций.

        Args:
            log_args (bool, optional): Флаг для логирования аргументов функции. По умолчанию True.
            log_result (bool, optional): Флаг для логирования результата функции. По умолчанию True.

        Returns:
            function: Декорированная функция.

        Использование:
        @logger.log_function_call(log_args=True, log_result=False)
        def my_function(arg1, arg2):
            # код функции
        """

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if log_args:
                    self._logger.info(f"Вызов функции {func.__name__} с аргументами: {args}, {kwargs}")
                else:
                    self._logger.info(f"Вызов функции {func.__name__}")

                result = func(*args, **kwargs)

                if log_result:
                    self._logger.info(f"Функция {func.__name__} завершила выполнение. Результат: {result}")
                else:
                    self._logger.info(f"Функция {func.__name__} завершила выполнение.")

                return result

            return wrapper

        return decorator

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._logger.critical(msg, *args, **kwargs)