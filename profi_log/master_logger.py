import logging
from logging.handlers import RotatingFileHandler
import os
import contextlib
import colorlog
import traceback
import smtplib
from email.message import EmailMessage
import functools
from typing import Optional, List, Callable, Any

class LoggerProxy:
    """
    Прокси-класс для объединения функциональности стандартного логгера и MasterLogger.
    """

    def __init__(self, logger: logging.Logger, master_logger: 'MasterLogger'):
        """
        Инициализация LoggerProxy.

        Args:
            logger (logging.Logger): Стандартный логгер Python.
            master_logger (MasterLogger): Экземпляр MasterLogger.
        """
        self._logger = logger
        self._master_logger = master_logger

    def __getattr__(self, name: str) -> Any:
        """
        Перехватывает обращения к атрибутам и методам.

        Args:
            name (str): Имя атрибута или метода.

        Returns:
            Any: Атрибут или метод из logger или master_logger.

        Raises:
            AttributeError: Если атрибут не найден ни в logger, ни в master_logger.
        """
        if hasattr(self._logger, name):
            return getattr(self._logger, name)
        elif hasattr(self._master_logger, name):
            return getattr(self._master_logger, name)
        raise AttributeError(f"'LoggerProxy' object has no attribute '{name}'")

class MasterLogger:
    """
    Продвинутый класс для настройки и управления логированием.
    """

    def __init__(self, log_file_name: str, name: Optional[str] = None, max_bytes: int = 100 * 1024 * 1024,
                 backup_count: int = 5, encoding: str = 'utf-8', level: str = 'INFO'):
        """
        Инициализация MasterLogger.

        Args:
            log_file_name (str): Имя файла для логов.
            name (Optional[str]): Имя логгера. Если не указано, используется корневой логгер.
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

        self._root_logger = logging.getLogger(name) if name else logging.getLogger()
        self.setup_file_logging()

    def setup_file_logging(self) -> None:
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
        self._root_logger.addHandler(handler)
        self._root_logger.setLevel(self.level)

    def setup_colored_console_logging(self, format_string: Optional[str] = None) -> None:
        """
        Настройка цветного консольного логирования.

        Args:
            format_string (Optional[str]): Строка форматирования для логов.
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
        self._root_logger.addHandler(handler)

    def get_logger(self, name: str) -> LoggerProxy:
        """
        Создает и возвращает именованный логгер.

        Args:
            name (str): Имя для нового логгера.

        Returns:
            LoggerProxy: Прокси-объект, объединяющий функциональность стандартного логгера и MasterLogger.
        """
        logger = logging.getLogger(name)
        logger.setLevel(self.level)
        return LoggerProxy(logger, self)

    @contextlib.contextmanager
    def temporary_log_level(self, level: str) -> None:
        """
        Контекстный менеджер для временного изменения уровня логирования.

        Args:
            level (str): Временный уровень логирования.

        Yields:
            None
        """
        old_level = self._root_logger.level
        self._root_logger.setLevel(getattr(logging, level.upper()))
        try:
            yield
        finally:
            self._root_logger.setLevel(old_level)

    def log_exception(self, message: str, exc_info: bool = True) -> None:
        """
        Логирование исключения с полной трассировкой стека.

        Args:
            message (str): Сообщение об ошибке.
            exc_info (bool): Флаг для включения информации об исключении. По умолчанию True.
        """
        if exc_info:
            self._root_logger.error(f"{message}\n{traceback.format_exc()}")
        else:
            self._root_logger.error(message)

    def log_function_call(self, log_args: bool = True, log_result: bool = True) -> Callable:
        """
        Декоратор для автоматического логирования вызовов функций.

        Args:
            log_args (bool): Флаг для логирования аргументов функции. По умолчанию True.
            log_result (bool): Флаг для логирования результата функции. По умолчанию True.

        Returns:
            Callable: Декоратор функции.
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if log_args:
                    self._root_logger.info(f"Вызов функции {func.__name__} с аргументами: {args}, {kwargs}")
                else:
                    self._root_logger.info(f"Вызов функции {func.__name__}")

                result = func(*args, **kwargs)

                if log_result:
                    self._root_logger.info(f"Функция {func.__name__} завершила выполнение. Результат: {result}")
                else:
                    self._root_logger.info(f"Функция {func.__name__} завершила выполнение.")

                return result
            return wrapper
        return decorator

    def setup_email_logging(self, smtp_server: str, port: int, sender: str, password: str, recipients: List[str],
                            subject_prefix: str = "Критическая ошибка") -> None:
        """
        Настройка отправки критических логов по электронной почте.

        Args:
            smtp_server (str): SMTP сервер.
            port (int): Порт SMTP сервера.
            sender (str): Email отправителя.
            password (str): Пароль отправителя.
            recipients (List[str]): Список получателей.
            subject_prefix (str): Префикс для темы письма. По умолчанию "Критическая ошибка".
        """
        class EmailHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
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
        self._root_logger.addHandler(handler)

    # Методы для прямого логирования
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._root_logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._root_logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._root_logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._root_logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._root_logger.critical(msg, *args, **kwargs)